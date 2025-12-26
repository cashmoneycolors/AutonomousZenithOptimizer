using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using System.Net.Http;
using System.Text;
using StackExchangeRedis = StackExchange.Redis;
using ZenithCoreSystem;
using ZenithCoreSystem.Adapters;
using ZenithCoreSystem.Core;
using ZenithCoreSystem.Modules;

var builder = Host.CreateApplicationBuilder(args);

try
{
    Console.OutputEncoding = Encoding.UTF8;
    Console.InputEncoding = Encoding.UTF8;
}
catch
{
    // Ignore: some hosts/terminals don't support changing encodings.
}

builder.Logging.ClearProviders();
builder.Logging.AddSimpleConsole(options =>
{
    options.SingleLine = true;
    options.TimestampFormat = "HH:mm:ss ";
});

builder.Services.Configure<OptimizerSettings>(builder.Configuration.GetSection("Optimizer"));

// Core infrastructure registrations
builder.Services.AddSingleton<IConnectionMultiplexer>(sp =>
{
    var options = sp.GetRequiredService<IOptions<OptimizerSettings>>().Value;

    if (!string.IsNullOrWhiteSpace(options.RedisConnectionString))
    {
        var multiplexer = StackExchangeRedis.ConnectionMultiplexer.Connect(options.RedisConnectionString);
        return new StackExchangeRedisConnection(multiplexer);
    }

    return new RedisMock();
});
builder.Services.AddSingleton<HoloKognitivesRepository>();
builder.Services.AddSingleton<ContextualMemoryHandler>();
builder.Services.AddSingleton<IProfitGuarantor_QML>(sp =>
{
    var settings = sp.GetRequiredService<IOptions<OptimizerSettings>>();
    var logger = sp.GetRequiredService<ILogger<QML_Python_Bridge>>();
    return new QML_Python_Bridge(settings.Value.SimulateQmlFailure, settings.Value.QmlEndpoint, logger);
});
builder.Services.AddSingleton<RegulatoryHyperAdaptor>();
builder.Services.AddSingleton<AetherArchitecture>();

// External adapters
builder.Services.AddSingleton<IHFT_AMAD_Adapter, HFT_AMAD_Adapter>();
builder.Services.AddSingleton<IGEF_MSA_Adapter, GEF_MSA_Adapter>();
builder.Services.AddSingleton<IECA_AHA_Adapter, ECA_AHA_Adapter>();

// Core orchestrator
builder.Services.AddSingleton<IAutonomousZenithOptimizer, AutonomousZenithOptimizer>();

using var host = builder.Build();
var optimizer = host.Services.GetRequiredService<IAutonomousZenithOptimizer>();
var settings = host.Services.GetRequiredService<IOptions<OptimizerSettings>>().Value;
var logger = host.Services.GetRequiredService<ILogger<Program>>();
// Live-Guardrails: verhindert "schein-live" Konfigurationen
var liveMode = settings.LiveMode || string.Equals(Environment.GetEnvironmentVariable("AZO_LIVE_MODE"), "true", StringComparison.OrdinalIgnoreCase);
if (liveMode)
{
    // sorgt dafuer, dass Adapter/Module (die ENV nutzen) konsistent reagieren
    Environment.SetEnvironmentVariable("AZO_LIVE_MODE", "true");

    static void EnsureHttpEndpoint(string endpoint, string source)
    {
        if (!Uri.TryCreate(endpoint, UriKind.Absolute, out var uri) ||
            !(uri.Scheme.Equals("http", StringComparison.OrdinalIgnoreCase) || uri.Scheme.Equals("https", StringComparison.OrdinalIgnoreCase)))
        {
            throw new InvalidOperationException($"LiveMode aktiv: Ungueltiger QML Endpoint ({source}). Erwartet absolute http(s) URL, erhalten: '{endpoint}'.");
        }
    }

    static void EnsureNotStub<TService>(IServiceProvider services, Type stubType, string message)
        where TService : notnull
    {
        var resolved = services.GetRequiredService<TService>();
        if (resolved is not null && resolved.GetType() == stubType)
        {
            throw new InvalidOperationException(message);
        }
    }

    if (settings.EnableDemoScenarios)
        throw new InvalidOperationException("LiveMode aktiv: EnableDemoScenarios muss false sein.");

    if (settings.SimulateQmlFailure)
        throw new InvalidOperationException("LiveMode aktiv: SimulateQmlFailure muss false sein.");

    var endpoint = string.IsNullOrWhiteSpace(settings.QmlEndpoint)
        ? Environment.GetEnvironmentVariable("AZO_QML_ENDPOINT")
        : settings.QmlEndpoint;

    if (string.IsNullOrWhiteSpace(endpoint))
        throw new InvalidOperationException("LiveMode aktiv: QML Endpoint fehlt (Optimizer:QmlEndpoint oder ENV AZO_QML_ENDPOINT).");

    EnsureHttpEndpoint(endpoint, string.IsNullOrWhiteSpace(settings.QmlEndpoint) ? "ENV AZO_QML_ENDPOINT" : "Optimizer:QmlEndpoint");

    // Fail-fast: LiveMode darf nicht mit Stub-Adaptern starten (sonst knallt es erst mitten im Zyklus)
    EnsureNotStub<IHFT_AMAD_Adapter>(
        host.Services,
        typeof(HFT_AMAD_Adapter),
        "LiveMode aktiv: IHFT_AMAD_Adapter ist ein Stub (HFT_AMAD_Adapter). Bitte echten Provider integrieren oder LiveMode deaktivieren."
    );

    EnsureNotStub<IGEF_MSA_Adapter>(
        host.Services,
        typeof(GEF_MSA_Adapter),
        "LiveMode aktiv: IGEF_MSA_Adapter ist ein Stub (GEF_MSA_Adapter). Bitte echte Text/LLM-Integration integrieren oder LiveMode deaktivieren."
    );

    EnsureNotStub<IECA_AHA_Adapter>(
        host.Services,
        typeof(ECA_AHA_Adapter),
        "LiveMode aktiv: IECA_AHA_Adapter ist ein Stub (ECA_AHA_Adapter). Bitte echte Order/CRM-Integration integrieren oder LiveMode deaktivieren."
    );
}

Console.WriteLine("--- ZQAN Ω: MAXIMALER SYSTEMSTART & API-INTEGRATION ---");
logger.LogInformation("[STATUS] HostBuilder hat den Zenith Controller mit allen Modulen registriert.");

var cts = new CancellationTokenSource();
Console.CancelKeyPress += (s, e) =>
{
    logger.LogWarning("Shutdown-Signal empfangen. Graceful Shutdown wird initiiert...");
    e.Cancel = true;
    cts.Cancel();
};

// Non-blocking Startup-Healthcheck: reduziert Überraschungen (Endpoint down) ohne 24/7 Betrieb zu stoppen.
try
{
    var configuredEndpoint = string.IsNullOrWhiteSpace(settings.QmlEndpoint)
        ? Environment.GetEnvironmentVariable("AZO_QML_ENDPOINT")
        : settings.QmlEndpoint;

    if (!string.IsNullOrWhiteSpace(configuredEndpoint))
    {
        using var http = new HttpClient { Timeout = TimeSpan.FromSeconds(2) };
        var navProbe = 0m;
        var probeUri = configuredEndpoint.Trim() + "?nav=" + navProbe;
        using var resp = await http.GetAsync(probeUri, cts.Token);
        if (!resp.IsSuccessStatusCode)
        {
            logger.LogWarning("QML Startup-Check: Endpoint antwortet mit {StatusCode}: {Endpoint}", (int)resp.StatusCode, configuredEndpoint);
        }
        else
        {
            logger.LogInformation("QML Startup-Check: Endpoint erreichbar: {Endpoint}", configuredEndpoint);
        }
    }
}
catch (Exception ex)
{
    logger.LogWarning(ex, "QML Startup-Check fehlgeschlagen (non-blocking). Weiter im 24/7 Modus.");
}

var iterationCount = 0;
var errorCount = 0;
var maxConsecutiveErrors = Math.Max(1, settings.MaxConsecutiveErrors);
var jitterMaxMs = Math.Max(0, settings.ErrorJitterMaxMilliseconds);
var rng = new Random();

try
{
    while (!cts.Token.IsCancellationRequested)
    {
        iterationCount++;
        logger.LogInformation($"\n========== ITERATION #{iterationCount} ==========");

        try
        {
            await optimizer.RunAutonomousGrowthStrategy();

            if (settings.EnableDemoScenarios)
            {
                logger.LogInformation("\n--- TEST: ECA/AHA Transaktion & Governance ---");

                var orderBlocked = new Order("ORD-ZQN-1", "001", "CUST_FR", "FR", 5000.00m, "PremiumLicense");
                logger.LogInformation("\n-> Teste Auftrag (FR) (Governance Gate ist permissiv):");
                await optimizer.ProcessIncomingOrder(orderBlocked);

                var orderAllowed = new Order("ORD-ZQN-2", "002", "CUST_DE", "DE", 999.00m, "PremiumLicense");
                logger.LogInformation("\n-> Teste erlaubten Auftrag (Governance Success - ECA/AHA):");
                await optimizer.ProcessIncomingOrder(orderAllowed);
            }

            errorCount = 0; // Reset bei erfolgreicher Iteration

            var delay = settings.CycleDelaySeconds > 0 ? settings.CycleDelaySeconds : 60;
            logger.LogInformation($"\n--- Zyklus abgeschlossen, nächste Iteration in {delay} Sekunden ---");
            await Task.Delay(TimeSpan.FromSeconds(delay), cts.Token);
        }
        catch (OperationCanceledException)
        {
            logger.LogInformation("Iteration abgebrochen (Shutdown).");
            break;
        }
        catch (Exception ex)
        {
            errorCount++;
            logger.LogError(ex, $"[FEHLER] Iteration #{iterationCount} fehlgeschlagen (Fehler {errorCount}/{maxConsecutiveErrors})");

            if (errorCount >= maxConsecutiveErrors)
            {
                logger.LogCritical($"KRITISCH: {maxConsecutiveErrors} aufeinanderfolgende Fehler. System geht in Cooldown (24/7 Betrieb) statt Shutdown.");

                // Cooldown statt Exit: 24/7 Betrieb, aber ohne Busy-Loop.
                var coolDownSeconds = Math.Max(1, settings.ErrorCooldownSeconds);
                var jitter = jitterMaxMs > 0 ? rng.Next(0, jitterMaxMs + 1) : 0;
                logger.LogWarning($"Cooldown fuer {coolDownSeconds} Sekunden... Danach neuer Versuch.");
                errorCount = 0;
                await Task.Delay(TimeSpan.FromSeconds(coolDownSeconds), cts.Token);
                if (jitter > 0)
                {
                    await Task.Delay(TimeSpan.FromMilliseconds(jitter), cts.Token);
                }
                continue;
            }

            // Exponential Backoff bei Fehlern
            var backoffCap = Math.Max(1, settings.ErrorBackoffMaxSeconds);
            var backoffSeconds = Math.Min(Math.Pow(2, errorCount), backoffCap);
            var retryJitter = jitterMaxMs > 0 ? rng.Next(0, jitterMaxMs + 1) : 0;
            logger.LogWarning($"Retry in {backoffSeconds} Sekunden... (jitter {retryJitter}ms)");
            await Task.Delay(TimeSpan.FromSeconds(backoffSeconds), cts.Token);
            if (retryJitter > 0)
            {
                await Task.Delay(TimeSpan.FromMilliseconds(retryJitter), cts.Token);
            }
        }
    }
}
catch (OperationCanceledException)
{
    logger.LogInformation("Shutdown abgeschlossen.");
}
catch (Exception ex)
{
    logger.LogCritical(ex, "FATALER FEHLER: System konnte nicht wiederhergestellt werden.");
    Environment.Exit(1);
}

logger.LogInformation($"\n--- ZQAN Ω SHUTDOWN ---\nIterationen: {iterationCount} | Fehler: {errorCount}");
await host.StopAsync();
Environment.Exit(0);


