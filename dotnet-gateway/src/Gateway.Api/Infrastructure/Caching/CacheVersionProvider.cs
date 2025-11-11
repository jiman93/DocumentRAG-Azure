using Gateway.Api.Configuration;
using Microsoft.Extensions.Caching.Distributed;
using Microsoft.Extensions.Options;

namespace Gateway.Api.Infrastructure.Caching;

public interface ICacheVersionProvider
{
  Task<string> GetChatVersionAsync(CancellationToken cancellationToken = default);
  Task BumpChatVersionAsync(CancellationToken cancellationToken = default);
}

public sealed class CacheVersionProvider : ICacheVersionProvider
{
  private const string ChatVersionKey = "cache:chat:version";
  private static readonly DistributedCacheEntryOptions VersionCacheOptions = new()
  {
    AbsoluteExpirationRelativeToNow = TimeSpan.FromDays(7)
  };

  private readonly IDistributedCache _cache;
  private readonly GatewayOptions _options;

  public CacheVersionProvider(IDistributedCache cache, IOptions<GatewayOptions> options)
  {
    _cache = cache;
    _options = options.Value;
  }

  public async Task<string> GetChatVersionAsync(CancellationToken cancellationToken = default)
  {
    if (!_options.EnableCaching)
    {
      return "caching-disabled";
    }

    var version = await _cache.GetStringAsync(ChatVersionKey, cancellationToken);
    if (!string.IsNullOrEmpty(version))
    {
      return version;
    }

    version = GenerateVersion();
    await _cache.SetStringAsync(ChatVersionKey, version, VersionCacheOptions, cancellationToken);
    return version;
  }

  public async Task BumpChatVersionAsync(CancellationToken cancellationToken = default)
  {
    if (!_options.EnableCaching)
    {
      return;
    }

    var version = GenerateVersion();
    await _cache.SetStringAsync(ChatVersionKey, version, VersionCacheOptions, cancellationToken);
  }

  private static string GenerateVersion() => Guid.NewGuid().ToString("N");
}


