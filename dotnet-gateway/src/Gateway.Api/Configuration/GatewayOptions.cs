namespace Gateway.Api.Configuration;

public class GatewayOptions
{
    public string? PythonRagApiUrl { get; set; }
    public bool EnableCaching { get; set; } = true;
    public int CacheExpirationMinutes { get; set; } = 5;
    public int DocumentListCacheMinutes { get; set; } = 5;
    public int ChatResponseCacheMinutes { get; set; } = 60;
    public long MaxRequestSizeBytes { get; set; } = 10_485_760;
}

