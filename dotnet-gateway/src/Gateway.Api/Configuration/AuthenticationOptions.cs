namespace Gateway.Api.Configuration;

public class AuthenticationOptions
{
  public bool Enabled { get; set; } = true;
  public string? Authority { get; set; }
  public string? Audience { get; set; }
  public bool ValidateIssuer { get; set; } = true;
  public bool ValidateAudience { get; set; } = true;
  public bool ValidateLifetime { get; set; } = true;
}

