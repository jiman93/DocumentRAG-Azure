using System.Text.Json;
using System.Text.Json.Serialization;

namespace Gateway.Api.Models.Chat;

public sealed class ChatMessage
{
    [JsonPropertyName("role")]
    public string Role { get; set; } = string.Empty;

    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;

    [JsonPropertyName("timestamp")]
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

public sealed class RagQueryRequest
{
    [JsonPropertyName("question")]
    public string Question { get; set; } = string.Empty;

    [JsonPropertyName("document_id")]
    public string? DocumentId { get; set; }

    [JsonPropertyName("conversation_id")]
    public string? ConversationId { get; set; }

    [JsonPropertyName("conversation_history")]
    public List<ChatMessage>? ConversationHistory { get; set; }

    [JsonPropertyName("top_k")]
    public int TopK { get; set; } = 3;

    [JsonPropertyName("temperature")]
    public double Temperature { get; set; } = 0.3;

    [JsonPropertyName("stream")]
    public bool Stream { get; set; }

    [JsonPropertyName("include_sources")]
    public bool IncludeSources { get; set; } = true;

    [JsonPropertyName("filters")]
    public JsonElement? Filters { get; set; }
}


