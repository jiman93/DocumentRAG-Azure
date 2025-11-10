namespace Gateway.Api.Configuration;

public class GatewayOptions
{
    public string? PythonRagApiUrl { get; set; }
    public bool EnableCaching { get; set; } = true;
    public int CacheExpirationMinutes { get; set; } = 5;
    public long MaxRequestSizeBytes { get; set; } = 10_485_760;
}

