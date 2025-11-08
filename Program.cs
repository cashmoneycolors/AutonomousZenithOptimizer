using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using ZenithCoreSystem;
using ZenithCoreSystem.Adapters;
using ZenithCoreSystem.Core;
using ZenithCoreSystem.Modules;

var builder = Host.CreateApplicationBuilder(args);

// Core infrastructure registrations
builder.Services.AddSingleton<IConnectionMultiplexer, RedisMock>();
builder.Services.AddSingleton<HoloKognitivesRepository>();
builder.Services.AddSingleton<ContextualMemoryHandler>();
builder.Services.AddSingleton<IProfitGuarantor_QML>(_ => new QML_Python_Bridge(simulateFailure: true));
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

await optimizer.RunAutonomousGrowthStrategy();

Console.WriteLine("\n--- TEST: ECA/AHA Transaktion & Governance ---");

var orderBlocked = new Order("ORD-ZQN-1", "001", "CUST_FR", "FR", 5000.00m, "PremiumLicense");
Console.WriteLine("\n-> Teste blockierten Auftrag (Governance Fail - RHA):");
await optimizer.ProcessIncomingOrder(orderBlocked);

var orderAllowed = new Order("ORD-ZQN-2", "002", "CUST_DE", "DE", 999.00m, "PremiumLicense");
Console.WriteLine("\n-> Teste erlaubten Auftrag (Governance Success - ECA/AHA):");
await optimizer.ProcessIncomingOrder(orderAllowed);

Console.WriteLine("\n--- HostBuilder Shutdown ---");
