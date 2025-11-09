using System;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using Xunit;
using ZenithCoreSystem;
using ZenithCoreSystem.Adapters;
using ZenithCoreSystem.Core;
using ZenithCoreSystem.Modules;

namespace ZenithCoreSystem.Tests
{
    public class AutonomousZenithOptimizerTests
    {
        [Fact]
        public async Task RunAutonomousGrowthStrategy_FallsBackAfterQmlFailures()
        {
            var failingQml = new AlwaysFailingQml();
            var hft = new RecordingHftAdapter();
            var gef = new RecordingGefAdapter();
            var eca = new RecordingEcaAdapter();
            var optimizer = CreateOptimizer(failingQml, hft, gef, eca);

            await optimizer.RunAutonomousGrowthStrategy();

            Assert.Equal(3, failingQml.CallCount);
            Assert.Equal("MAINTAIN_LEVEL:1.0", failingQml.LastReportedAction);
            Assert.Equal(0, hft.CallCount);
        }

        [Fact]
        public async Task ProcessIncomingOrder_BlocksNonCompliantPremiumOrder()
        {
            var qml = new NoOpQml();
            var hft = new RecordingHftAdapter();
            var gef = new RecordingGefAdapter();
            var eca = new RecordingEcaAdapter();
            var optimizer = CreateOptimizer(qml, hft, gef, eca);

            var nonCompliantOrder = new Order("ORD-TEST-1", "A-1", "CUST-FR", "FR", 5000m, "PremiumLicense");

            await optimizer.ProcessIncomingOrder(nonCompliantOrder);

            Assert.False(eca.WasCalled);
        }

        [Fact]
        public async Task ProcessIncomingOrder_AllowsCompliantPremiumOrder()
        {
            var qml = new NoOpQml();
            var hft = new RecordingHftAdapter();
            var gef = new RecordingGefAdapter();
            var eca = new RecordingEcaAdapter();
            var optimizer = CreateOptimizer(qml, hft, gef, eca);

            var compliantOrder = new Order("ORD-TEST-2", "A-2", "CUST-DE", "DE", 900m, "PremiumLicense");

            await optimizer.ProcessIncomingOrder(compliantOrder);

            Assert.True(eca.WasCalled);
            Assert.Equal(1, eca.CallCount);
        }

        private static AutonomousZenithOptimizer CreateOptimizer(
            IProfitGuarantor_QML qml,
            IHFT_AMAD_Adapter hft,
            IGEF_MSA_Adapter gef,
            IECA_AHA_Adapter eca,
            ILogger<AutonomousZenithOptimizer>? logger = null,
            OptimizerSettings? settings = null)
        {
            var redis = new RedisMock();
            var repository = new HoloKognitivesRepository(redis);
            var contextHandler = new ContextualMemoryHandler(repository);
            var architecture = new AetherArchitecture();
            var regulator = new RegulatoryHyperAdaptor();

            logger ??= NullLogger<AutonomousZenithOptimizer>.Instance;
            settings ??= new OptimizerSettings { QmlBaseDelayMilliseconds = 0 };
            var options = Options.Create(settings);

            return new AutonomousZenithOptimizer(qml, architecture, regulator, hft, gef, eca, contextHandler, options, logger);
        }

        private sealed class RecordingHftAdapter : IHFT_AMAD_Adapter
        {
            public int CallCount { get; private set; }

            public Task<decimal> ExecuteTrade(string symbol, decimal amount, string direction)
            {
                CallCount++;
                return Task.FromResult(amount);
            }
        }

        private sealed class RecordingGefAdapter : IGEF_MSA_Adapter
        {
            public int CallCount { get; private set; }

            public Task<string> GenerateText(string prompt, string styleGuide)
            {
                CallCount++;
                return Task.FromResult("ok");
            }
        }

        private sealed class RecordingEcaAdapter : IECA_AHA_Adapter
        {
            public int CallCount { get; private set; }
            public bool WasCalled => CallCount > 0;

            public Task<bool> SubmitOrder(Order order, string supplierID)
            {
                CallCount++;
                return Task.FromResult(true);
            }
        }

        private sealed class NoOpQml : IProfitGuarantor_QML
        {
            public string? LastReportedAction { get; private set; }

            public Task<string> GetNAVOptimizedDecision(DRL_StateVector currentVector)
                => Task.FromResult("MAINTAIN_LEVEL:1.0");

            public Task ReportPerformanceFeedback(string vector, decimal roasScore, string actionTaken)
            {
                LastReportedAction = actionTaken;
                return Task.CompletedTask;
            }
        }

        private sealed class AlwaysFailingQml : IProfitGuarantor_QML
        {
            public int CallCount { get; private set; }
            public string? LastReportedAction { get; private set; }

            public async Task<string> GetNAVOptimizedDecision(DRL_StateVector currentVector)
            {
                CallCount++;
                throw new TimeoutException("Simulated QML failure");
            }

            public Task ReportPerformanceFeedback(string vector, decimal roasScore, string actionTaken)
            {
                LastReportedAction = actionTaken;
                return Task.CompletedTask;
            }
        }
    }
}
