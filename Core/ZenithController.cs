using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Diagnostics;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using ZenithCoreSystem.Adapters;
using ZenithCoreSystem.Modules;

namespace ZenithCoreSystem.Core
{
    public class AutonomousZenithOptimizer : IAutonomousZenithOptimizer
    {
        private readonly IProfitGuarantor_QML _qml;
        private readonly AetherArchitecture _arch;
        private readonly RegulatoryHyperAdaptor _rha;
        private readonly IHFT_AMAD_Adapter _hftAdapter;
        private readonly IGEF_MSA_Adapter _gefAdapter;
        private readonly IECA_AHA_Adapter _ecaAdapter;
        private readonly ContextualMemoryHandler _chm;
        private readonly ILogger<AutonomousZenithOptimizer> _logger;
        private readonly OptimizerSettings _settings;

        public AutonomousZenithOptimizer(
            IProfitGuarantor_QML qml,
            AetherArchitecture arch,
            RegulatoryHyperAdaptor rha,
            IHFT_AMAD_Adapter hftAdapter,
            IGEF_MSA_Adapter gefAdapter,
            IECA_AHA_Adapter ecaAdapter,
            ContextualMemoryHandler chm,
            IOptions<OptimizerSettings> settings,
            ILogger<AutonomousZenithOptimizer> logger)
        {
            _qml = qml;
            _arch = arch;
            _rha = rha;
            _hftAdapter = hftAdapter;
            _gefAdapter = gefAdapter;
            _ecaAdapter = ecaAdapter;
            _chm = chm;
            _settings = settings.Value;
            _logger = logger;
        }

        private async Task<string> ExecuteQMLWithRetry(DRL_StateVector stateVector)
        {
            int maxAttempts = Math.Max(1, _settings.QmlRetryCount);
            for (int i = 0; i < maxAttempts; i++)
            {
                try
                {
                    return await _qml.GetNAVOptimizedDecision(stateVector);
                }
                catch (Exception ex)
                {
                    if (i == maxAttempts - 1)
                    {
                        _logger.LogCriticalError($"MAX RETRY erreicht. Fallback aktiv. Grund: {ex.Message}", "QML_DRL_Agent");
                        return "MAINTAIN_LEVEL:1.0";
                    }

                    int delay = Math.Max(0, _settings.QmlBaseDelayMilliseconds) * (i + 1);
                    if (delay > 0)
                    {
                        await Task.Delay(delay);
                    }
                }
            }

            return "MAINTAIN_LEVEL:1.0";
        }

        public async Task RunAutonomousGrowthStrategy()
        {
            Guid cycleId = Guid.NewGuid();
            DateTime startTime = DateTime.UtcNow;

            _logger.LogAutonomousCycle("Starte autonomen Wachstumszyklus (DRL-Basis).", new Dictionary<string, object>
            {
                { "CorrelationID", cycleId.ToString() },
                { "Stage", "INIT" }
            });

            var stateVector = new DRL_StateVector(
                MarketROAS_Score: 4.5m,
                CurrentMarketSpend: 10000.00m,
                PredictedNAV: 130000.00m,
                RH_ComplianceScore: _rha.PerformComplianceMock() ? 0.99 : 0.75,
                GSF_Complexity: 0.85,
                HyperCache_LatencyMs: 0.003,
                ScalingFactor: 1.0,
                TotalNFTsMinted: 500);

            string decision = await ExecuteQMLWithRetry(stateVector);

            if (decision.StartsWith("SCALE_UP:", StringComparison.OrdinalIgnoreCase))
            {
                decimal factor = decimal.Parse(decision.Split(':')[1]);
                decimal tradeAmount = 100000.00m * factor;
                await _hftAdapter.ExecuteTrade("ETH/USD", tradeAmount, "BUY");
            }

            if (stateVector.RH_ComplianceScore > _settings.ComplianceThreshold)
            {
                await _gefAdapter.GenerateText("Erstelle einen Marketing-Text fuer das neue NFT-Produkt.", "Corporate Identity VECTRA");
            }

            long latencyMs = (long)(DateTime.UtcNow - startTime).TotalMilliseconds;
            await _qml.ReportPerformanceFeedback(stateVector.ToString(), 4.5m, decision);

            _logger.LogAutonomousCycle("Zyklus abgeschlossen. DRL-Aktion ausgefuehrt.", new Dictionary<string, object>
            {
                { "CorrelationID", cycleId.ToString() },
                { "ActionTaken", decision },
                { "EndToEndLatencyMs", latencyMs }
            });
        }

        public async Task ProcessIncomingOrder(Order order)
        {
            Console.WriteLine($"\n[AZO] Starte Prozess fuer Auftrag {order.OrderID}...");

            if (!_rha.PerformLegalIntegrityCheck(order))
            {
                _logger.LogCriticalError($"Auftrag {order.OrderID} wegen Legal Integrity Check (LIC) fehlgeschlagen. Blockiere Transaktion.", "RHA");
                _arch.RouteLowLatencyEvent($"Auftrag {order.OrderID} wegen LIC-Fehler blockiert.");
                return;
            }

            await _chm.DeliverPreventiveContext($"OrderProcessing_{order.ProductType}");

            if (order.ProductType == "PremiumLicense")
            {
                bool success = await _ecaAdapter.SubmitOrder(order, "Supplier-Alpha");
                if (success)
                {
                    _arch.RouteLowLatencyEvent($"Auftrag {order.OrderID} erfolgreich ueber ECA/AHA abgewickelt.");
                }
                else
                {
                    _logger.LogCriticalError($"Fehler bei der API-Uebermittlung fuer {order.OrderID}.", "ECA/AHA");
                }
            }
        }

        private async Task RunPythonAgent()
        {
            try
            {
                var process = new Process
                {
                    StartInfo = new ProcessStartInfo
                    {
                        FileName = "python",
                        Arguments = "agent.py",
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        UseShellExecute = false,
                        CreateNoWindow = true,
                        WorkingDirectory = AppDomain.CurrentDomain.BaseDirectory
                    }
                };

                process.Start();
                string output = await process.StandardOutput.ReadToEndAsync();
                string error = await process.StandardError.ReadToEndAsync();
                await process.WaitForExitAsync();

                _logger.LogInformation($"Python Agent Output: {output}");
                if (!string.IsNullOrEmpty(error))
                {
                    _logger.LogError($"Python Agent Error: {error}");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError($"Failed to run Python agent: {ex.Message}");
            }
        }
    }
}
