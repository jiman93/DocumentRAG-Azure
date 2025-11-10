using Gateway.Api.Configuration;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.Extensions.Caching.Distributed;
using Microsoft.Extensions.Options;
using System.Text.Json;

namespace Gateway.Api.Controllers;

[ApiController]
[Route("api/v1/[controller]")]
[EnableRateLimiting("fixed")]
[Authorize]
public class DocumentsController : ControllerBase
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly IDistributedCache _cache;
    private readonly ILogger<DocumentsController> _logger;
    private readonly GatewayOptions _gatewayOptions;

    public DocumentsController(
        IHttpClientFactory httpClientFactory,
        IDistributedCache cache,
        ILogger<DocumentsController> logger,
        IOptions<GatewayOptions> gatewayOptions)
    {
        _httpClientFactory = httpClientFactory;
        _cache = cache;
        _logger = logger;
        _gatewayOptions = gatewayOptions.Value;
    }

    /// <summary>
    /// Upload a document for processing
    /// </summary>
    [HttpPost("upload")]
    [RequestSizeLimit(10_485_760)] // 10MB
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status429TooManyRequests)]
    public async Task<IActionResult> UploadDocument(IFormFile file)
    {
        if (file == null || file.Length == 0)
        {
            return BadRequest(new { error = "No file provided" });
        }

        var maxSize = _gatewayOptions.MaxRequestSizeBytes;
        if (file.Length > maxSize)
        {
            return BadRequest(new { error = $"File size exceeds maximum of {maxSize / 1_048_576}MB" });
        }

        _logger.LogInformation("Uploading document: {FileName}, Size: {FileSize}", 
            file.FileName, file.Length);

        try
        {
            var client = _httpClientFactory.CreateClient("PythonRagApi");
            
            using var content = new MultipartFormDataContent();
            using var fileStream = file.OpenReadStream();
            using var streamContent = new StreamContent(fileStream);
            
            streamContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(
                file.ContentType);
            content.Add(streamContent, "file", file.FileName);

            var response = await client.PostAsync("/api/v1/documents/upload", content);
            
            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError("Upload failed: {StatusCode}, {Error}", 
                    response.StatusCode, errorContent);
                return StatusCode((int)response.StatusCode, 
                    new { error = "Document upload failed" });
            }

            var result = await response.Content.ReadAsStringAsync();
            
            // Invalidate documents cache
            if (_gatewayOptions.EnableCaching)
            {
                await _cache.RemoveAsync("documents:list");
            }
            
            return Ok(JsonSerializer.Deserialize<object>(result));
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "HTTP error during document upload");
            return StatusCode(StatusCodes.Status503ServiceUnavailable, 
                new { error = "RAG service unavailable" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error uploading document");
            return StatusCode(StatusCodes.Status500InternalServerError, 
                new { error = "Internal server error" });
        }
    }

    /// <summary>
    /// List all documents
    /// </summary>
    [HttpGet]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public async Task<IActionResult> ListDocuments()
    {
        var cacheKey = "documents:list";
        
        if (_gatewayOptions.EnableCaching)
        {
            var cachedData = await _cache.GetStringAsync(cacheKey);
            if (!string.IsNullOrEmpty(cachedData))
            {
                _logger.LogInformation("Returning cached documents list");
                return Ok(JsonSerializer.Deserialize<object>(cachedData));
            }
        }

        try
        {
            var client = _httpClientFactory.CreateClient("PythonRagApi");
            var response = await client.GetAsync("/api/v1/documents");
            
            if (!response.IsSuccessStatusCode)
            {
                return StatusCode((int)response.StatusCode, 
                    new { error = "Failed to retrieve documents" });
            }

            var result = await response.Content.ReadAsStringAsync();
            
            if (_gatewayOptions.EnableCaching)
            {
                var expirationMinutes = Math.Max(1, _gatewayOptions.CacheExpirationMinutes);
                var cacheOptions = new DistributedCacheEntryOptions
                {
                    AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(expirationMinutes)
                };
                await _cache.SetStringAsync(cacheKey, result, cacheOptions);
            }
            
            return Ok(JsonSerializer.Deserialize<object>(result));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error listing documents");
            return StatusCode(StatusCodes.Status500InternalServerError, 
                new { error = "Internal server error" });
        }
    }

    /// <summary>
    /// Delete a document
    /// </summary>
    [HttpDelete("{documentId}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> DeleteDocument(string documentId)
    {
        _logger.LogInformation("Deleting document: {DocumentId}", documentId);

        try
        {
            var client = _httpClientFactory.CreateClient("PythonRagApi");
            var response = await client.DeleteAsync($"/api/v1/documents/{documentId}");
            
            if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
            {
                return NotFound(new { error = "Document not found" });
            }
            
            if (!response.IsSuccessStatusCode)
            {
                return StatusCode((int)response.StatusCode, 
                    new { error = "Failed to delete document" });
            }

            // Invalidate cache
            if (_gatewayOptions.EnableCaching)
            {
                await _cache.RemoveAsync("documents:list");
            }
            
            var result = await response.Content.ReadAsStringAsync();
            return Ok(JsonSerializer.Deserialize<object>(result));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting document");
            return StatusCode(StatusCodes.Status500InternalServerError, 
                new { error = "Internal server error" });
        }
    }
}
