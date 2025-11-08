using System;
using System.Threading.Tasks;
using ZenithCoreSystem;

namespace ZenithCoreSystem.Adapters
{
    public class ECA_AHA_Adapter : IECA_AHA_Adapter
    {
        public async Task<bool> SubmitOrder(Order order, string supplierID)
        {
            Console.WriteLine($"[AHA/ECA] Order {order.OrderID} an Supplier {supplierID} via CRM/API gesendet.");
            await Task.Delay(50);
            return true;
        }
    }
}
