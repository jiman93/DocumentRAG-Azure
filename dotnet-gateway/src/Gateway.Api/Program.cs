using Gateway.Api.Configuration;
using Gateway.Api.Infrastructure.Authentication;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.IdentityModel.Tokens;
using Polly;
using Polly.Extensions.Http;
using Serilog;
using System.Threading.RateLimiting;
using HealthChecks.Uris;
using Microsoft.OpenApi.Models;
using GatewayAuthenticationOptions = Gateway.Api.Configuration.AuthenticationOptions;

var builder = WebApplication.CreateBuilder(args);

// Configure Serilog
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration)
    .Enrich.FromLogContext()
    .WriteTo.Console()
    .WriteTo.ApplicationInsights(
        builder.Configuration["ApplicationInsights:InstrumentationKey"],
        TelemetryConverter.Traces)
    .CreateLogger();

builder.Host.UseSerilog();

// Add services
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new Microsoft.OpenApi.Models.OpenApiInfo
    {
        Title = "Document RAG Gateway API",
        Version = "v1"
    });
});

builder.Services.Configure<GatewayOptions>(builder.Configuration.GetSection("Gateway"));
builder.Services.Configure<RateLimitingOptions>(builder.Configuration.GetSection("RateLimiting"));
builder.Services.Configure<GatewayAuthenticationOptions>(builder.Configuration.GetSection("Authentication"));

var gatewayOptions = builder.Configuration.GetSection("Gateway").Get<GatewayOptions>() ?? new GatewayOptions();
var rateLimitingOptions = builder.Configuration.GetSection("RateLimiting").Get<RateLimitingOptions>() ?? new RateLimitingOptions();
var authenticationOptions = builder.Configuration.GetSection("Authentication").Get<GatewayAuthenticationOptions>() ?? new GatewayAuthenticationOptions();
var rateLimiterWindow = TimeSpan.TryParse(rateLimitingOptions.Window, out var parsedWindow)
    ? parsedWindow
    : TimeSpan.FromMinutes(1);

// Authentication & Authorization
builder.Services.AddAuthorization();

if (authenticationOptions.Enabled &&
    !string.IsNullOrWhiteSpace(authenticationOptions.Authority) &&
    !string.IsNullOrWhiteSpace(authenticationOptions.Audience))
{
    builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
        .AddJwtBearer(options =>
        {
            options.Authority = authenticationOptions.Authority;
            options.Audience = authenticationOptions.Audience;
            options.TokenValidationParameters = new TokenValidationParameters
            {
                ValidateIssuer = authenticationOptions.ValidateIssuer,
                ValidateAudience = authenticationOptions.ValidateAudience,
                ValidateLifetime = authenticationOptions.ValidateLifetime
            };
        });
}
else
{
    builder.Services.AddAuthentication(options =>
    {
        options.DefaultAuthenticateScheme = "AllowAll";
        options.DefaultChallengeScheme = "AllowAll";
    }).AddScheme<AuthenticationSchemeOptions, AllowAnonymousAuthenticationHandler>("AllowAll", _ => { });
}

// CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
    {
        policy.WithOrigins(builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>() ?? [])
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials();
    });
});

// Redis / Distributed Cache
var redisConnection = builder.Configuration.GetConnectionString("Redis");
if (gatewayOptions.EnableCaching)
{
    if (!string.IsNullOrEmpty(redisConnection))
    {
        builder.Services.AddStackExchangeRedisCache(options =>
        {
            options.Configuration = redisConnection;
            options.InstanceName = "RagGateway_";
        });
    }
    else
    {
        builder.Services.AddDistributedMemoryCache();
    }
}
else
{
    builder.Services.AddDistributedMemoryCache();
}

// Rate Limiting
builder.Services.AddRateLimiter(options =>
{
    if (rateLimitingOptions.EnableRateLimiting)
    {
        options.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(context =>
        {
            var userIdentifier = context.User.Identity?.Name ?? context.Connection.RemoteIpAddress?.ToString() ?? "anonymous";

            return RateLimitPartition.GetFixedWindowLimiter(
                partitionKey: userIdentifier,
                factory: _ => new FixedWindowRateLimiterOptions
                {
                    PermitLimit = rateLimitingOptions.PermitLimit,
                    Window = rateLimiterWindow,
                    QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                    QueueLimit = rateLimitingOptions.QueueLimit
                });
        });

        options.AddPolicy("fixed", context =>
        {
            var identifier = context.User.Identity?.Name ?? context.Connection.RemoteIpAddress?.ToString() ?? "anonymous";
            return RateLimitPartition.GetFixedWindowLimiter(
                partitionKey: identifier,
                factory: _ => new FixedWindowRateLimiterOptions
                {
                    PermitLimit = rateLimitingOptions.PermitLimit,
                    Window = rateLimiterWindow,
                    QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                    QueueLimit = rateLimitingOptions.QueueLimit
                });
        });
    }
    else
    {
        options.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(_ =>
            RateLimitPartition.GetNoLimiter("global"));

        options.AddPolicy("fixed", _ =>
            RateLimitPartition.GetNoLimiter("fixed"));
    }

    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    options.OnRejected = async (context, cancellationToken) =>
    {
        context.HttpContext.Response.StatusCode = StatusCodes.Status429TooManyRequests;
        await context.HttpContext.Response.WriteAsJsonAsync(
            new { error = "Rate limit exceeded. Please try again later." },
            cancellationToken: cancellationToken);
    };
});

// HTTP Client for Python RAG API
var pythonApiBaseUrl = gatewayOptions.PythonRagApiUrl ?? "http://localhost:8000";
builder.Services.AddHttpClient("PythonRagApi", client =>
{
    client.BaseAddress = new Uri(pythonApiBaseUrl);
    client.Timeout = TimeSpan.FromSeconds(120);
})
.AddTransientHttpErrorPolicy(policy =>
    policy.WaitAndRetryAsync(3, retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt))))
.AddTransientHttpErrorPolicy(policy =>
    policy.CircuitBreakerAsync(5, TimeSpan.FromSeconds(30)));

// Health Checks
var healthChecks = builder.Services.AddHealthChecks();

if (gatewayOptions.EnableCaching && !string.IsNullOrEmpty(redisConnection))
{
    healthChecks.AddRedis(redisConnection, name: "redis", tags: new[] { "ready" });
}

healthChecks.AddUrlGroup(new Uri($"{pythonApiBaseUrl.TrimEnd('/')}/health"),
                 name: "python-rag-api",
                 tags: new[] { "ready" });

builder.Services.AddHealthChecksUI()
    .AddInMemoryStorage();

// Application Insights
builder.Services.AddApplicationInsightsTelemetry();

var app = builder.Build();

// Configure pipeline
if (!app.Environment.IsDevelopment())
{
    app.UseHttpsRedirection();
}

app.UseSwagger();
app.UseSwaggerUI(options =>
{
    options.SwaggerEndpoint("/swagger/v1/swagger.json", "Document RAG Gateway API v1");
    options.RoutePrefix = "swagger";
});

app.UseRouting();
app.UseCors("AllowFrontend");
app.UseRateLimiter();

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

// Health check endpoints
app.MapHealthChecks("/health");
app.MapHealthChecks("/health/ready", new Microsoft.AspNetCore.Diagnostics.HealthChecks.HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});
app.MapHealthChecks("/health/live", new Microsoft.AspNetCore.Diagnostics.HealthChecks.HealthCheckOptions
{
    Predicate = _ => false
});

app.MapHealthChecksUI();

app.Run();
