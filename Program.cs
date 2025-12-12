using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using StackExchangeRedis = StackExchange.Redis;
using ZenithCoreSystem;
using ZenithCoreSystem.Adapters;
using ZenithCoreSystem.Core;
using ZenithCoreSystem.Modules;

var builder = Host.CreateApplicationBuilder(args);

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
	return new QML_Python_Bridge(settings.Value.SimulateQmlFailure);
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

Console.WriteLine("--- ZQAN Ω: MAXIMALER SYSTEMSTART & API-INTEGRATION ---");
logger.LogInformation("[STATUS] HostBuilder hat den Zenith Controller mit allen Modulen registriert.");

var cts = new CancellationTokenSource();
Console.CancelKeyPress += (s, e) =>
{
    logger.LogWarning("Shutdown-Signal empfangen. Graceful Shutdown wird initiiert...");
    e.Cancel = true;
    cts.Cancel();
};

var iterationCount = 0;
var errorCount = 0;
const int maxConsecutiveErrors = 5;

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
                logger.LogInformation("\n-> Teste blockierten Auftrag (Governance Fail - RHA):");
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
                logger.LogCritical($"KRITISCH: {maxConsecutiveErrors} aufeinanderfolgende Fehler. System wird heruntergefahren.");
                throw;
            }

            // Exponential Backoff bei Fehlern
            var backoffSeconds = Math.Min(Math.Pow(2, errorCount), 300); // Max 5 Minuten
            logger.LogWarning($"Retry in {backoffSeconds} Sekunden...");
            await Task.Delay(TimeSpan.FromSeconds(backoffSeconds), cts.Token);
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
