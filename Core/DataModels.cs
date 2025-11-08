using System.Collections.Generic;

namespace ZenithCoreSystem
{
    public record Asset(string AssetID, string Name, string ArtistHistory, Dictionary<string, bool> LicenseMap, int Quota);

    public record Order(string OrderID, string AssetID, string CustomerID, string DestinationCountry, decimal Price, string ProductType);

    public record DRL_StateVector(
        decimal MarketROAS_Score,
        decimal CurrentMarketSpend,
        decimal PredictedNAV,
        double RH_ComplianceScore,
        double GSF_Complexity,
        double HyperCache_LatencyMs,
        double ScalingFactor,
        int TotalNFTsMinted)
    {
        public override string ToString() =>
            $"ROAS:{MarketROAS_Score:F2};SPEND:{CurrentMarketSpend:F0};PMI_PRED:{PredictedNAV:F0};RHA_SCORE:{RH_ComplianceScore:F2};GSF_COMPX:{GSF_Complexity:F2};CACHE_LATENCY:{HyperCache_LatencyMs:F4};SCALE_FACTOR:{ScalingFactor:F2};NFT_COUNT:{TotalNFTsMinted}";
    }
}
