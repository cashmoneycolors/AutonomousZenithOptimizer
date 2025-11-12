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

Console.WriteLine("--- ZQAN Ω: MAXIMALER SYSTEMSTART & API-INTEGRATION ---");
Console.WriteLine("[STATUS] HostBuilder hat den Zenith Controller mit allen Modulen registriert.");

while (true)
{
    await optimizer.RunAutonomousGrowthStrategy();

    Console.WriteLine("\n--- TEST: ECA/AHA Transaktion & Governance ---");

    var orderBlocked = new Order("ORD-ZQN-1", "001", "CUST_FR", "FR", 5000.00m, "PremiumLicense");
    Console.WriteLine("\n-> Teste blockierten Auftrag (Governance Fail - RHA):");
    await optimizer.ProcessIncomingOrder(orderBlocked);

    var orderAllowed = new Order("ORD-ZQN-2", "002", "CUST_DE", "DE", 999.00m, "PremiumLicense");
    Console.WriteLine("\n-> Teste erlaubten Auftrag (Governance Success - ECA/AHA):");
    await optimizer.ProcessIncomingOrder(orderAllowed);

    Console.WriteLine("\n--- Zyklus abgeschlossen, nächste Iteration in 60 Sekunden ---");
    await Task.Delay(60000); // 60 Sekunden warten
}
