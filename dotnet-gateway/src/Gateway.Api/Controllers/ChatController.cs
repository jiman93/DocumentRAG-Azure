using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Gateway.Api.Configuration;
using Gateway.Api.Infrastructure.Caching;
using Gateway.Api.Models.Chat;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.Extensions.Caching.Distributed;
using Microsoft.Extensions.Options;

namespace Gateway.Api.Controllers;

[ApiController]
[Route("api/v1/[controller]")]
[EnableRateLimiting("fixed")]
[Authorize]
public class ChatController : ControllerBase
{
    private const string CachePrefix = "chat:query";

    private static readonly JsonSerializerOptions SerializerOptions = new()
    {
        DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull,
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase
    };

    private readonly IHttpClientFactory _httpClientFactory;
    private readonly IDistributedCache _cache;
    private readonly ILogger<ChatController> _logger;
    private readonly GatewayOptions _gatewayOptions;
    private readonly ICacheVersionProvider _cacheVersionProvider;

    public ChatController(
        IHttpClientFactory httpClientFactory,
        IDistributedCache cache,
        ILogger<ChatController> logger,
        IOptions<GatewayOptions> gatewayOptions,
        ICacheVersionProvider cacheVersionProvider)
    {
        _httpClientFactory = httpClientFactory;
        _cache = cache;
        _logger = logger;
        _gatewayOptions = gatewayOptions.Value;
        _cacheVersionProvider = cacheVersionProvider;
    }

    [HttpPost("query")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status429TooManyRequests)]
    public async Task<IActionResult> QueryAsync([FromBody] RagQueryRequest request, CancellationToken cancellationToken)
    {
        if (request is null || string.IsNullOrWhiteSpace(request.Question))
        {
            return BadRequest(new { error = "Question is required." });
        }

        if (request.Stream)
        {
            _logger.LogWarning("Stream=true is not supported by the gateway. Question: {Question}", request.Question);
            return BadRequest(new { error = "Streaming responses are not supported by the gateway." });
        }

        var client = _httpClientFactory.CreateClient("PythonRagApi");
        var requestPayload = JsonSerializer.Serialize(request, SerializerOptions);

        string? cacheKey = null;
        if (_gatewayOptions.EnableCaching)
        {
            var version = await _cacheVersionProvider.GetChatVersionAsync(cancellationToken);
            var hash = ComputeHash(requestPayload);
            cacheKey = $"{CachePrefix}:{version}:{hash}";

            var cachedResponse = await _cache.GetStringAsync(cacheKey, cancellationToken);
            if (!string.IsNullOrEmpty(cachedResponse))
            {
                _logger.LogInformation("Returning cached chat response for hash {Hash}", hash);
                return Content(cachedResponse, "application/json");
            }
        }

        using var content = new StringContent(requestPayload, Encoding.UTF8, "application/json");
        var response = await client.PostAsync("/chat/query", content, cancellationToken);
        var responseBody = await response.Content.ReadAsStringAsync(cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            _logger.LogWarning("Chat query failed: {StatusCode} {Body}", response.StatusCode, responseBody);

            object? errorPayload = null;
            try
            {
                if (!string.IsNullOrWhiteSpace(responseBody))
                {
                    errorPayload = JsonSerializer.Deserialize<object>(responseBody);
                }
            }
            catch (JsonException)
            {
                // fallback to default payload
            }

            return StatusCode(
                (int)response.StatusCode,
                errorPayload ?? new { error = "Failed to process chat query." });
        }

        if (cacheKey is not null)
        {
            var minutes = _gatewayOptions.ChatResponseCacheMinutes > 0
                ? _gatewayOptions.ChatResponseCacheMinutes
                : Math.Max(1, _gatewayOptions.CacheExpirationMinutes);

            var cacheOptions = new DistributedCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(minutes)
            };

            await _cache.SetStringAsync(cacheKey, responseBody, cacheOptions, cancellationToken);
        }

        return Content(responseBody, "application/json");
    }

    [HttpGet("history/{conversationId}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetHistoryAsync(string conversationId, CancellationToken cancellationToken)
    {
        if (string.IsNullOrWhiteSpace(conversationId))
        {
            return BadRequest(new { error = "conversationId is required." });
        }

        var client = _httpClientFactory.CreateClient("PythonRagApi");
        var response = await client.GetAsync($"/chat/history/{conversationId}", cancellationToken);
        var responseBody = await response.Content.ReadAsStringAsync(cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            _logger.LogWarning("Failed to retrieve conversation history {ConversationId}: {StatusCode} {Body}", conversationId, response.StatusCode, responseBody);
            object? payload = null;
            try
            {
                if (!string.IsNullOrWhiteSpace(responseBody))
                {
                    payload = JsonSerializer.Deserialize<object>(responseBody);
                }
            }
            catch (JsonException)
            {
                // ignore
            }

            return StatusCode(
                (int)response.StatusCode,
                payload ?? new { error = "Failed to retrieve conversation history." });
        }

        return Content(responseBody, "application/json");
    }

    [HttpGet("conversations")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public async Task<IActionResult> ListConversationsAsync([FromQuery] int limit = 50, [FromQuery] int offset = 0, CancellationToken cancellationToken = default)
    {
        if (limit <= 0)
        {
            return BadRequest(new { error = "limit must be greater than zero." });
        }

        var client = _httpClientFactory.CreateClient("PythonRagApi");
        var response = await client.GetAsync($"/chat/conversations?limit={limit}&offset={offset}", cancellationToken);
        var responseBody = await response.Content.ReadAsStringAsync(cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            _logger.LogWarning("Failed to list conversations: {StatusCode} {Body}", response.StatusCode, responseBody);
            object? payload = null;
            try
            {
                if (!string.IsNullOrWhiteSpace(responseBody))
                {
                    payload = JsonSerializer.Deserialize<object>(responseBody);
                }
            }
            catch (JsonException)
            {
                // ignore
            }

            return StatusCode(
                (int)response.StatusCode,
                payload ?? new { error = "Failed to retrieve conversations." });
        }

        return Content(responseBody, "application/json");
    }

    private static string ComputeHash(string payload)
    {
        using var sha = SHA256.Create();
        var bytes = Encoding.UTF8.GetBytes(payload);
        var hashBytes = sha.ComputeHash(bytes);
        return Convert.ToHexString(hashBytes);
    }
}


