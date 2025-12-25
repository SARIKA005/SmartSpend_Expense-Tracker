import os
import json
import requests
import random
from datetime import datetime
from typing import Dict, List, Optional

class SmartFinanceAI:
    """Smart financial AI advisor that analyzes your spending patterns"""
    
    def __init__(self):
        self.analysis_cache = {}
        
    def analyze_finances(self, expense_data: Dict, total_expenses: float, 
                        savings: float, goals: List, analysis_type: str) -> str:
        """
        Analyze finances and provide smart recommendations
        """
        # Create a unique cache key
        cache_key = f"{hash(str(expense_data))}_{total_expenses}_{savings}_{analysis_type}"
        
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        # Generate comprehensive analysis
        analysis = self._generate_analysis(expense_data, total_expenses, savings, goals, analysis_type)
        
        # Cache the analysis
        self.analysis_cache[cache_key] = analysis
        return analysis
    
    def _generate_analysis(self, expense_data: Dict, total_expenses: float,
                          savings: float, goals: List, analysis_type: str) -> str:
        """Generate intelligent financial analysis"""
        
        # Start building the analysis
        analysis = "## 🧠 Smart Financial Analysis\n\n"
        
        # Calculate key metrics
        savings_rate = (savings / total_expenses * 100) if total_expenses > 0 else 0
        
        # 1. Overall Financial Health
        analysis += "### 📊 Your Financial Health\n"
        
        if savings_rate >= 20:
            analysis += "✅ **Excellent!** Your savings rate is healthy. Keep this momentum!\n\n"
        elif savings_rate >= 10:
            analysis += "👍 **Good progress!** You're saving consistently. Aim for 20% savings rate.\n\n"
        else:
            analysis += "📈 **Room for improvement.** Try to save at least 10% of your expenses each month.\n\n"
        
        # 2. Expense Analysis
        if expense_data:
            analysis += "### 💸 Spending Analysis\n"
            
            # Find top categories
            sorted_expenses = sorted(expense_data.items(), key=lambda x: x[1], reverse=True)
            
            if len(sorted_expenses) >= 3:
                top1_cat, top1_amt = sorted_expenses[0]
                top2_cat, top2_amt = sorted_expenses[1]
                top3_cat, top3_amt = sorted_expenses[2]
                
                top1_pct = (top1_amt / total_expenses * 100) if total_expenses > 0 else 0
                top3_total = sum([amt for _, amt in sorted_expenses[:3]])
                top3_pct = (top3_total / total_expenses * 100) if total_expenses > 0 else 0
                
                analysis += f"• **Top 3 categories** account for {top3_pct:.1f}% of spending\n"
                analysis += f"• **{top1_cat}** is your largest expense at {top1_pct:.1f}%\n\n"
                
                if top1_pct > 40:
                    analysis += f"💡 **Insight:** Consider ways to reduce {top1_cat} expenses by 15% next month.\n\n"
            
            # Identify potential savings
            if total_expenses > 0:
                average_expense = total_expenses / len(expense_data) if expense_data else 0
                
                # Find high-value opportunities
                high_value_cats = []
                for category, amount in expense_data.items():
                    pct = (amount / total_expenses * 100)
                    if pct > 25:  # Categories over 25% of total
                        potential_saving = amount * 0.15  # 15% reduction
                        high_value_cats.append((category, potential_saving))
                
                if high_value_cats:
                    analysis += "### 💰 Quick Win Opportunities\n"
                    for category, potential in high_value_cats[:2]:  # Show top 2
                        analysis += f"• Reduce **{category}** by 15% to save **₹{potential:,.0f}** monthly\n"
                    analysis += "\n"
        
        # 3. Goals Progress
        active_goals = [g for g in goals if g.get('status') == 'active']
        if active_goals:
            analysis += "### 🎯 Goals Progress\n"
            
            for goal in active_goals[:2]:  # Show top 2
                name = goal.get('name', 'Goal')
                current = goal.get('current_amount', 0)
                target = goal.get('target_amount', 1)
                progress = (current / target * 100) if target > 0 else 0
                
                analysis += f"**{name}:** {progress:.1f}% complete\n"
                
                if progress < 100:
                    remaining = target - current
                    analysis += f"  → Need ₹{remaining:,.0f} more to reach target\n"
                
                if 0 < progress < 30:
                    analysis += f"  📌 **Tip:** Break this goal into weekly targets\n"
                elif 30 <= progress < 70:
                    analysis += f"  📌 **Tip:** Stay consistent! You're halfway there\n"
                elif progress >= 70:
                    analysis += f"  📌 **Tip:** Almost there! Finish strong\n"
                
                analysis += "\n"
        
        # 4. Personalized Recommendations
        analysis += "### 🚀 Personalized Action Plan\n"
        
        # Generate smart recommendations based on data
        recommendations = self._generate_recommendations(expense_data, total_expenses, savings, goals, analysis_type)
        
        for i, rec in enumerate(recommendations[:4], 1):  # Show top 4
            analysis += f"{i}. {rec}\n"
        
        analysis += "\n"
        
        # 5. This Week's Focus
        analysis += "### 🗓️ This Week's Focus\n"
        weekly_focus = random.choice([
            "Track every expense for 7 days",
            "Review one subscription service",
            "Save ₹500 extra this week",
            "Cook meals at home 5 days this week",
            "Walk or use public transport 3 times"
        ])
        analysis += f"**Your challenge:** {weekly_focus}\n\n"
        
        # 6. Encouragement
        analysis += "### 💪 Remember\n"
        encouragement = random.choice([
            "Financial success is built one smart decision at a time.",
            "Small, consistent improvements lead to big results.",
            "You're in control of your financial future.",
            "Every rupee saved today is an investment in your tomorrow.",
            "Progress, not perfection, is the goal."
        ])
        analysis += f"*{encouragement}*\n\n"
        
        # Add timestamp
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        analysis += f"*Analysis generated: {now}*"
        
        return analysis
    
    def _generate_recommendations(self, expense_data: Dict, total_expenses: float,
                                 savings: float, goals: List, analysis_type: str) -> List[str]:
        """Generate personalized recommendations"""
        
        recommendations = []
        
        # Based on savings rate
        savings_rate = (savings / total_expenses * 100) if total_expenses > 0 else 0
        
        if savings_rate < 10:
            recommendations.extend([
                "Set up automatic transfers of ₹2,000 to savings on payday",
                "Use the 24-hour rule for purchases over ₹1,000",
                "Review monthly subscriptions and cancel one unused service",
                "Pack lunch 3 times a week to save on food costs"
            ])
        elif savings_rate < 20:
            recommendations.extend([
                "Increase your automatic savings by ₹500 this month",
                "Invest ₹1,000 in a low-cost index fund",
                "Create a 6-month emergency fund as your next goal",
                "Review insurance policies for better rates"
            ])
        else:
            recommendations.extend([
                "Consider increasing investments by 10% this quarter",
                "Diversify your savings into different asset classes",
                "Plan for tax-efficient investment strategies",
                "Set up a separate fund for learning new skills"
            ])
        
        # Based on expense patterns
        if expense_data:
            largest_cat = max(expense_data.items(), key=lambda x: x[1])[0] if expense_data else ""
            largest_amt = max(expense_data.values()) if expense_data else 0
            largest_pct = (largest_amt / total_expenses * 100) if total_expenses > 0 else 0
            
            if largest_pct > 30:
                recommendations.append(f"Reduce {largest_cat} spending by 15% through better planning")
        
        # Based on goals
        active_goals = [g for g in goals if g.get('status') == 'active']
        if active_goals:
            for goal in active_goals[:1]:
                name = goal.get('name', 'your goal')
                current = goal.get('current_amount', 0)
                target = goal.get('target_amount', 1)
                
                if target > current:
                    weekly_needed = (target - current) / 4  # 4 weeks in a month
                    recommendations.append(f"Save ₹{weekly_needed:,.0f} weekly for '{name}'")
        
        # General smart tips
        smart_tips = [
            "Use cash for discretionary spending to stay within budget",
            "Round up purchases to nearest ₹100 and save the difference",
            "Negotiate better rates on bills and subscriptions annually",
            "Batch similar tasks to save time and money",
            "Invest in quality items that last longer",
            "Learn one new money-saving skill each month",
            "Review your financial plan every Sunday evening",
            "Celebrate small financial wins to stay motivated"
        ]
        
        # Add 2 random smart tips
        recommendations.extend(random.sample(smart_tips, 2))
        
        return recommendations
    
    def get_quick_insight(self, expense_data: Dict) -> str:
        """Generate a quick insight about spending patterns"""
        if not expense_data:
            return "Start tracking expenses to get personalized insights!"
        
        total = sum(expense_data.values())
        largest_cat, largest_amt = max(expense_data.items(), key=lambda x: x[1])
        largest_pct = (largest_amt / total * 100) if total > 0 else 0
        
        insights = [
            f"Your biggest expense is **{largest_cat}** at {largest_pct:.1f}% of total spending",
            f"Consider reducing **{largest_cat}** by 10% to save ₹{largest_amt*0.1:,.0f} monthly",
            f"Top 3 categories account for most of your spending. Review them weekly",
            f"Every ₹100 saved in {largest_cat} adds up to ₹1,200 annually"
        ]
        
        return random.choice(insights)

# Global instance
smart_ai = SmartFinanceAI()

def get_financial_analysis(expense_summary: Dict, total_expenses: float,
                          total_savings: float, goals: List,
                          analysis_type: str = "Comprehensive Analysis") -> str:
    """
    Get smart financial analysis
    """
    return smart_ai.analyze_finances(
        expense_summary, total_expenses, total_savings, goals, analysis_type
    )