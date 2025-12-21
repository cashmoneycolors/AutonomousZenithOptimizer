using System;
using System.Threading.Tasks;
using ZenithCoreSystem;

namespace ZenithCoreSystem.Adapters
{
    public class GEF_MSA_Adapter : IGEF_MSA_Adapter
    {
        public async Task<string> GenerateText(string prompt, string styleGuide)
        {
            if (string.Equals(Environment.GetEnvironmentVariable("AZO_LIVE_MODE"), "true", StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("LiveMode aktiv, aber GEF_MSA_Adapter ist ein Stub. Bitte echte LLM/Text-API integrieren (kein Console+Delay).");
            }

            Console.WriteLine($"[MSA/GEF] KI-Anfrage (Style: {styleGuide}) wird ausgefuehrt...");
            await Task.Delay(100);
            return $"KI-Output: {prompt.Substring(0, Math.Min(15, prompt.Length))}... (Genehmigt durch Governance)";
        }
    }
}
