using System;
using System.Collections.Generic;
using System.Threading.Tasks;
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

        public AutonomousZenithOptimizer(
            IProfitGuarantor_QML qml,
            AetherArchitecture arch,
            RegulatoryHyperAdaptor rha,
            IHFT_AMAD_Adapter hftAdapter,
            IGEF_MSA_Adapter gefAdapter,
            IECA_AHA_Adapter ecaAdapter,
            ContextualMemoryHandler chm)
        {
            _qml = qml;
            _arch = arch;
            _rha = rha;
            _hftAdapter = hftAdapter;
            _gefAdapter = gefAdapter;
            _ecaAdapter = ecaAdapter;
            _chm = chm;
        }

        private async Task<string> ExecuteQMLWithRetry(DRL_StateVector stateVector)
        {
            for (int i = 0; i < 3; i++)
            {
                try
                {
                    return await _qml.GetNAVOptimizedDecision(stateVector);
                }
                catch (Exception ex)
                {
                    if (i == 2)
                    {
                        ZenithLogger.LogCriticalError($"MAX RETRY erreicht. Fallback aktiv. Grund: {ex.Message}", "QML_DRL_Agent");
                        return "MAINTAIN_LEVEL:1.0";
                    }

                    await Task.Delay(500 * (i + 1));
                }
            }

            return "MAINTAIN_LEVEL:1.0";
        }

        public async Task RunAutonomousGrowthStrategy()
        {
            Guid cycleId = Guid.NewGuid();
            DateTime startTime = DateTime.UtcNow;

            ZenithLogger.LogAutonomousCycle("Starte autonomen Wachstumszyklus (DRL-Basis).", new Dictionary<string, object>
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
                decimal tradeAmount = 50000.00m * factor;
                await _hftAdapter.ExecuteTrade("ETH/USD", tradeAmount, "BUY");
            }

            if (stateVector.RH_ComplianceScore > 0.9)
            {
                await _gefAdapter.GenerateText("Erstelle einen Marketing-Text fuer das neue NFT-Produkt.", "Corporate Identity VECTRA");
            }

            long latencyMs = (long)(DateTime.UtcNow - startTime).TotalMilliseconds;
            await _qml.ReportPerformanceFeedback(stateVector.ToString(), 4.5m, decision);

            ZenithLogger.LogAutonomousCycle("Zyklus abgeschlossen. DRL-Aktion ausgefuehrt.", new Dictionary<string, object>
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
                ZenithLogger.LogCriticalError($"Auftrag {order.OrderID} wegen Legal Integrity Check (LIC) fehlgeschlagen. Blockiere Transaktion.", "RHA");
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
                    ZenithLogger.LogCriticalError($"Fehler bei der API-Uebermittlung fuer {order.OrderID}.", "ECA/AHA");
                }
            }
        }
    }
}
