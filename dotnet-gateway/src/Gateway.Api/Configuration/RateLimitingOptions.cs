namespace Gateway.Api.Configuration;

public class RateLimitingOptions
{
    public bool EnableRateLimiting { get; set; } = true;
    public int PermitLimit { get; set; } = 100;
    public string Window { get; set; } = "00:01:00";
    public int QueueLimit { get; set; } = 2;
}

