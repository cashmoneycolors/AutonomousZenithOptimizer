#!/usr/bin/env python3
"""
QUANTUM SUBSCRIPTION MODUL - Abonnement-Management System
Advanced Subscription Billing & Lifecycle Management
"""
import sys
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class QuantumSubscriptionModul:
    """QUANTUM Subscription Management mit intelligentem Billing"""

    def __init__(self):
        self.subscriptions = {}
        self.billing_history = {}
        self.pricing_tiers = self._initialize_pricing()
        self.discount_engine = True
        self.churn_prevention_active = True

        print("[QUANTUM SUBSCRIPTION] Subscription Management initialized")
        print("[QUANTUM SUBSCRIPTION] Pricing Tiers: {}".format(len(self.pricing_tiers)))
        print("[QUANTUM SUBSCRIPTION] Churn Prevention: {}".format("Active" if self.churn_prevention_active else "Inactive"))

    def _initialize_pricing(self) -> Dict[str, Any]:
        """Initialize subscription pricing tiers"""
        return {
            'starter': {
                'name': 'Starter',
                'monthly_price': 29.99,
                'yearly_price': 299.99,
                'features': ['basic_ai', '10gb_storage', '5_projects', 'email_support'],
                'limits': {'api_calls': 5000, 'users': 1, 'bandwidth': 50},
                'churn_risk': 0.15  # 15% monthly churn
            },
            'professional': {
                'name': 'Professional',
                'monthly_price': 79.99,
                'yearly_price': 799.99,
                'features': ['advanced_ai', '100gb_storage', '25_projects', 'priority_support', 'analytics'],
                'limits': {'api_calls': 50000, 'users': 5, 'bandwidth': 200},
                'churn_risk': 0.08  # 8% monthly churn
            },
            'enterprise': {
                'name': 'Enterprise',
                'monthly_price': 249.99,
                'yearly_price': 2499.99,
                'features': ['full_suite', 'unlimited_storage', 'unlimited_projects', '24_7_support', 'custom_features'],
                'limits': {'api_calls': -1, 'users': -1, 'bandwidth': -1},  # Unlimited
                'churn_risk': 0.03  # 3% monthly churn
            },
            'vip_quantum': {
                'name': 'VIP Quantum',
                'monthly_price': 999.99,
                'yearly_price': 9999.99,
                'features': ['quantum_priority', 'dedicated_support', 'early_access', 'custom_development', 'white_label'],
                'limits': {'api_calls': -1, 'users': -1, 'bandwidth': -1},
                'churn_risk': 0.01  # 1% monthly churn
            }
        }

    def create_quantum_subscription(self, customer_id: str, plan_type: str,
                                   billing_cycle: str = 'monthly',
                                   promo_code: Optional[str] = None) -> Dict[str, Any]:
        """Erstelle quantum subscription mit intelligenten Defaults"""

        subscription_id = f"SUB_Q_{random.randint(1000000, 9999999)}"
        plan_config = self.pricing_tiers.get(plan_type)

        if not plan_config:
            return {'success': False, 'error': f'Invalid plan type: {plan_type}'}

        # Calculate pricing with discounts
        base_price = plan_config[f'{billing_cycle}_price']
        discount_amount = self._apply_promo_discount(base_price, promo_code) if promo_code else 0
        final_price = base_price - discount_amount

        # Generate trial period for new customers
        has_trial = plan_type in ['starter', 'professional']
        trial_days = 14 if has_trial else 0

        subscription = {
            'subscription_id': subscription_id,
            'customer_id': customer_id,
            'plan_type': plan_type,
            'billing_cycle': billing_cycle,
            'status': 'trial' if has_trial else 'active',
            'created_at': datetime.now().isoformat(),
            'trial_end': (datetime.now() + timedelta(days=trial_days)).isoformat() if has_trial else None,
            'current_period_start': datetime.now().isoformat(),
            'current_period_end': self._calculate_period_end(billing_cycle),
            'cancel_at_period_end': False,
            'base_price': base_price,
            'discount_amount': discount_amount,
            'final_price': final_price,
            'currency': 'USD',
            'payment_method': None,
            'billing_attempts': 0,
            'failed_payments': 0,
            'usage_metrics': self._initialize_usage_metrics(plan_config),
            'churn_risk_score': plan_config['churn_risk']
        }

        self.subscriptions[subscription_id] = subscription

        return {
            'success': True,
            'subscription_id': subscription_id,
            'plan_details': plan_config,
            'pricing': {
                'base_price': base_price,
                'discount': discount_amount,
                'final_price': final_price,
                'billing_cycle': billing_cycle
            },
            'trial_info': {
                'has_trial': has_trial,
                'trial_days': trial_days
            },
            'next_billing_date': subscription['current_period_end']
        }

    def _apply_promo_discount(self, base_price: float, promo_code: str) -> float:
        """Apply promotional discount"""
        promo_discounts = {
            'SAVE20': 0.20,  # 20% off
            'QUANTUM10': 0.10,  # 10% off
            'WELCOME50': min(50, base_price * 0.50),  # $50 or 50% off, whichever smaller
            'ENTERPRISE25': 0.25  # 25% off for enterprise
        }

        discount_rate = promo_discounts.get(promo_code.upper(), 0)
        return base_price * discount_rate

    def _calculate_period_end(self, billing_cycle: str) -> str:
        """Calculate subscription period end date"""
        now = datetime.now()
        if billing_cycle == 'monthly':
            next_date = now + timedelta(days=30)
        elif billing_cycle == 'yearly':
            next_date = now + timedelta(days=365)
        elif billing_cycle == 'weekly':
            next_date = now + timedelta(days=7)
        else:
            next_date = now + timedelta(days=30)

        return next_date.isoformat()

    def _initialize_usage_metrics(self, plan_config: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize usage metrics for subscription tracking"""
        return {
            'api_calls_used': 0,
            'api_calls_limit': plan_config['limits']['api_calls'],
            'storage_used_gb': 0,
            'storage_limit_gb': plan_config['limits']['bandwidth'] if plan_config['limits']['bandwidth'] != -1 else 99999,
            'projects_created': 0,
            'projects_limit': plan_config['limits']['users'] * 5 if plan_config['limits']['users'] != -1 else 99999,
            'bandwidth_used_gb': 0,
            'bandwidth_limit_gb': plan_config['limits']['bandwidth'] if plan_config['limits']['bandwidth'] != -1 else 99999,
            'usage_reset_at': self._calculate_period_end('monthly'),  # Reset monthly
            'last_usage_update': datetime.now().isoformat()
        }

    def update_subscription_usage(self, subscription_id: str, usage_update: Dict[str, Any]) -> Dict[str, Any]:
        """Update subscription usage metrics"""

        if subscription_id not in self.subscriptions:
            return {'success': False, 'error': 'Subscription not found'}

        subscription = self.subscriptions[subscription_id]
        usage_metrics = subscription['usage_metrics']

        # Update usage values
        for metric, value in usage_update.items():
            if metric in usage_metrics:
                if metric.endswith('_used') or metric.endswith('_used_gb'):
                    usage_metrics[metric] += value
                    usage_metrics[metric] = max(0, usage_metrics[metric])  # Prevent negative

        usage_metrics['last_usage_update'] = datetime.now().isoformat()

        # Check usage limits and generate warnings
        warnings = self._check_usage_limits(subscription)

        return {
            'success': True,
            'updated_metrics': usage_metrics,
            'usage_warnings': warnings,
            'limit_exceeded': any(w['severity'] == 'exceeded' for w in warnings),
            'upgrade_suggestion': self._suggest_upgrade(subscription) if warnings else None
        }

    def _check_usage_limits(self, subscription: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check subscription usage against limits"""
        usage = subscription['usage_metrics']
        plan_limits = self.pricing_tiers[subscription['plan_type']]['limits']
        warnings = []

        # API Calls Check
        if plan_limits['api_calls'] != -1:
            api_usage_percent = (usage['api_calls_used'] / plan_limits['api_calls']) * 100
            if api_usage_percent >= 100:
                warnings.append({
                    'type': 'api_calls',
                    'severity': 'exceeded',
                    'message': f"API call limit exceeded: {usage['api_calls_used']}/{plan_limits['api_calls']}",
                    'usage_percent': api_usage_percent
                })
            elif api_usage_percent >= 90:
                warnings.append({
                    'type': 'api_calls',
                    'severity': 'warning',
                    'message': f"API call usage high: {usage['api_calls_used']}/{plan_limits['api_calls']} ({api_usage_percent:.1f}%)",
                    'usage_percent': api_usage_percent
                })

        # Storage Check
        if plan_limits['bandwidth'] != -1:
            storage_usage_percent = (usage['storage_used_gb'] / plan_limits['bandwidth']) * 100
            if storage_usage_percent >= 100:
                warnings.append({
                    'type': 'storage',
                    'severity': 'exceeded',
                    'message': f"Storage limit exceeded: {usage['storage_used_gb']:.1f}GB/{plan_limits['bandwidth']}GB",
                    'usage_percent': storage_usage_percent
                })
            elif storage_usage_percent >= 85:
                warnings.append({
                    'type': 'storage',
                    'severity': 'warning',
                    'message': f"Storage usage high: {usage['storage_used_gb']:.1f}GB/{plan_limits['bandwidth']}GB ({storage_usage_percent:.1f}%)",
                    'usage_percent': storage_usage_percent
                })

        return warnings

    def _suggest_upgrade(self, subscription: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Suggest upgrade based on usage patterns"""
        current_plan = subscription['plan_type']
        usage = subscription['usage_metrics']

        # Calculate upgrade need score
        need_score = 0

        api_limit = self.pricing_tiers[current_plan]['limits']['api_calls']
        if api_limit != -1 and usage['api_calls_used'] > api_limit * 0.8:
            need_score += 2

        storage_limit = self.pricing_tiers[current_plan]['limits']['bandwidth']
        if storage_limit != -1 and usage['storage_used_gb'] > storage_limit * 0.8:
            need_score += 2

        # Suggest upgrades based on need
        if need_score >= 3:
            if current_plan == 'starter':
                suggested_plan = 'professional'
            elif current_plan == 'professional':
                suggested_plan = 'enterprise'
            else:
                return None

            return {
                'suggested_plan': suggested_plan,
                'reason': 'Usage limits frequently exceeded',
                'estimated_savings': 'Upgrade could reduce overage costs',
                'monthly_price_difference': self.pricing_tiers[suggested_plan]['monthly_price'] - self.pricing_tiers[current_plan]['monthly_price']
            }

        return None

    def process_subscription_billing(self, subscription_id: str) -> Dict[str, Any]:
        """Process subscription billing cycle"""

        if subscription_id not in self.subscriptions:
            return {'success': False, 'error': 'Subscription not found'}

        subscription = self.subscriptions[subscription_id]

        # Skip if cancelled at period end
        if subscription.get('cancel_at_period_end'):
            return {
                'success': True,
                'billing_status': 'cancelled_at_period_end',
                'next_action': 'subscription_will_cancel'
            }

        # Attempt payment
        payment_result = self._process_payment(subscription)

        if payment_result['success']:
            # Move to next billing period
            subscription['current_period_start'] = subscription['current_period_end']
            subscription['current_period_end'] = self._calculate_period_end(subscription['billing_cycle'])
            subscription['billing_attempts'] = 0

            # Reset usage for monthly plans
            if subscription['billing_cycle'] == 'monthly':
                subscription['usage_metrics'] = self._initialize_usage_metrics(self.pricing_tiers[subscription['plan_type']])

            # Record billing event
            billing_event = {
                'subscription_id': subscription_id,
                'billing_date': datetime.now().isoformat(),
                'amount_charged': subscription['final_price'],
                'payment_method': subscription.get('payment_method', 'unknown'),
                'billing_cycle': subscription['billing_cycle'],
                'status': 'completed'
            }

            if subscription_id not in self.billing_history:
                self.billing_history[subscription_id] = []
            self.billing_history[subscription_id].append(billing_event)

            return {
                'success': True,
                'billing_status': 'completed',
                'amount_charged': subscription['final_price'],
                'next_billing_date': subscription['current_period_end'],
                'billing_id': billing_event
            }
        else:
            # Payment failed
            subscription['failed_payments'] += 1
            subscription['billing_attempts'] += 1

            if subscription['failed_payments'] >= 3:
                subscription['status'] = 'past_due'

            return {
                'success': False,
                'billing_status': 'payment_failed',
                'failure_reason': payment_result.get('error', 'Payment declined'),
                'retry_count': subscription['billing_attempts'],
                'subscription_status': subscription['status'],
                'next_retry_date': (datetime.now() + timedelta(days=3)).isoformat() if subscription['billing_attempts'] < 3 else None
            }

    def _process_payment(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment for subscription"""
        # Simulate payment processing (90% success rate)
        success_probability = 0.9 if subscription['failed_payments'] == 0 else 0.7  # Lower success for past failures

        success = random.random() < success_probability

        if success:
            return {
                'success': True,
                'transaction_id': f"TX_{random.randint(1000000000, 9999999999)}",
                'amount_processed': subscription['final_price']
            }
        else:
            error_messages = [
                'Card declined',
                'Insufficient funds',
                'Payment method expired',
                'Bank error',
                'Transaction timeout'
            ]
            return {
                'success': False,
                'error': random.choice(error_messages)
            }

    def cancel_subscription(self, subscription_id: str, cancel_immediately: bool = False,
                           cancellation_reason: str = 'customer_request') -> Dict[str, Any]:
        """Cancel subscription"""

        if subscription_id not in self.subscriptions:
            return {'success': False, 'error': 'Subscription not found'}

        subscription = self.subscriptions[subscription_id]

        if cancel_immediately:
            subscription['status'] = 'cancelled'
            subscription['cancelled_at'] = datetime.now().isoformat()
            subscription['cancellation_reason'] = cancellation_reason

            # Calculate prorated refund
            days_remaining = self._calculate_days_remaining(subscription)
            total_days = 30 if subscription['billing_cycle'] == 'monthly' else 365
            refund_amount = (subscription['final_price'] / total_days) * days_remaining

            return {
                'success': True,
                'cancellation_type': 'immediate',
                'refund_amount': refund_amount,
                'final_billing_date': datetime.now().isoformat(),
                'subscription_status': 'cancelled'
            }
        else:
            subscription['cancel_at_period_end'] = True

            return {
                'success': True,
                'cancellation_type': 'end_of_period',
                'final_billing_date': subscription['current_period_end'],
                'subscription_status': 'active_until_period_end'
            }

    def _calculate_days_remaining(self, subscription: Dict[str, Any]) -> int:
        """Calculate days remaining in current billing period"""
        end_date = datetime.fromisoformat(subscription['current_period_end'])
        days_remaining = max(0, (end_date - datetime.now()).days)
        return days_remaining

    def get_subscription_analytics(self) -> Dict[str, Any]:
        """Get comprehensive subscription analytics"""

        total_subscriptions = len(self.subscriptions)
        active_subscriptions = len([s for s in self.subscriptions.values() if s['status'] in ['active', 'trial']])
        cancelled_subscriptions = len([s for s in self.subscriptions.values() if s['status'] == 'cancelled'])

        # Calculate revenue metrics
        total_mrr = sum(s['final_price'] for s in self.subscriptions.values()
                       if s['status'] in ['active', 'trial'] and s['billing_cycle'] == 'monthly')
        total_arr = total_mrr * 12

        # Plan distribution
        plan_distribution = {}
        for subscription in self.subscriptions.values():
            plan = subscription['plan_type']
            plan_distribution[plan] = plan_distribution.get(plan, 0) + 1

        # Churn analysis
        churn_rate = cancelled_subscriptions / max(1, total_subscriptions)

        # Billing success rate
        total_billing_attempts = sum(s['billing_attempts'] for s in self.subscriptions.values())
        successful_bills = total_subscriptions - len([s for s in self.subscriptions.values() if s.get('failed_payments', 0) > 0])
        billing_success_rate = successful_bills / max(1, total_subscriptions)

        return {
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'cancelled_subscriptions': cancelled_subscriptions,
            'trial_subscriptions': len([s for s in self.subscriptions.values() if s['status'] == 'trial']),
            'revenue_metrics': {
                'monthly_recurring_revenue': total_mrr,
                'annual_recurring_revenue': total_arr,
                'average_revenue_per_user': total_mrr / max(1, active_subscriptions)
            },
            'plan_distribution': plan_distribution,
            'churn_analysis': {
                'churn_rate': churn_rate,
                'billing_success_rate': billing_success_rate,
                'average_lifespan_days': self._calculate_average_lifespan()
            },
            'top_cancellation_reasons': self._analyze_cancellation_reasons()
        }

    def _calculate_average_lifespan(self) -> float:
        """Calculate average subscription lifespan"""
        lifespans = []

        for subscription in self.subscriptions.values():
            created_at = datetime.fromisoformat(subscription['created_at'])
            ended_at = datetime.now()

            if subscription['status'] == 'cancelled' and 'cancelled_at' in subscription:
                ended_at = datetime.fromisoformat(subscription['cancelled_at'])

            lifespan_days = (ended_at - created_at).days
            lifespans.append(lifespan_days)

        return sum(lifespans) / max(1, len(lifespans)) if lifespans else 0

    def _analyze_cancellation_reasons(self) -> Dict[str, int]:
        """Analyze cancellation reasons"""
        reasons = {}

        for subscription in self.subscriptions.values():
            if subscription['status'] == 'cancelled':
                reason = subscription.get('cancellation_reason', 'not_specified')
                reasons[reason] = reasons.get(reason, 0) + 1

        # Return top 5 reasons
        sorted_reasons = sorted(reasons.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_reasons[:5])

# Global Subscription Module Instance
quantum_subscription_modul = QuantumSubscriptionModul()

def create_subscription(customer_id: str, plan_type: str, billing_cycle: str = 'monthly', promo_code=None):
    """Create new subscription"""
    return quantum_subscription_modul.create_quantum_subscription(customer_id, plan_type, billing_cycle, promo_code)

def update_usage(subscription_id: str, usage_update: Dict[str, Any]):
    """Update subscription usage"""
    return quantum_subscription_modul.update_subscription_usage(subscription_id, usage_update)

def process_billing(subscription_id: str):
    """Process billing cycle"""
    return quantum_subscription_modul.process_subscription_billing(subscription_id)

def cancel_subscription(subscription_id: str, cancel_immediately: bool = False, reason: str = 'customer_request'):
    """Cancel subscription"""
    return quantum_subscription_modul.cancel_subscription(subscription_id, cancel_immediately, reason)

def get_subscription_analytics():
    """Get subscription analytics"""
    return quantum_subscription_modul.get_subscription_analytics()

if __name__ == "__main__":
    print("QUANTUM SUBSCRIPTION MODUL - Advanced Subscription Management")
    print("=" * 80)

    print("[QUANTUM SUBSCRIPTION] Testing Subscription System...")

    # Create subscription
    subscription_result = create_subscription(
        customer_id="CUST_001",
        plan_type="professional",
        billing_cycle="monthly",
        promo_code="WELCOME50"
    )

    if subscription_result['success']:
        print("Subscription Created: {}".format(subscription_result['subscription_id']))
        print("Final Price: ${:.2f}/{}".format(subscription_result['pricing']['final_price'],
                                             subscription_result['pricing']['billing_cycle']))
        print("Plan: {}".format(subscription_result['plan_details']['name']))

    # Update usage
    subscription_id = subscription_result['subscription_id']
    usage_result = update_usage(subscription_id, {
        'api_calls_used': 15000,
        'storage_used_gb': 75,
        'projects_created': 12
    })

    if not usage_result['success']:
        print("Usage Update Failed")
    else:
        print("Usage Updated - Warnings: {}".format(len(usage_result['usage_warnings'])))

    # Process billing
    billing_result = process_billing(subscription_id)
    if billing_result['success']:
        print("Billing Processed: ${:.2f}".format(billing_result['amount_charged']))
    else:
        print("Billing Failed: {}".format(billing_result['billing_status']))

    # Get analytics
    analytics = get_subscription_analytics()
    print("Analytics: {} total subscriptions, {:.2f}% billing success rate".format(
        analytics['total_subscriptions'],
        analytics['churn_analysis']['billing_success_rate'] * 100
    ))

    print("\n[QUANTUM SUBSCRIPTION] SUBSCRIPTION MANAGEMENT OPERATIONAL!")
    print("Advanced Subscription Billing - Enterprise Revenue Management Ready")
