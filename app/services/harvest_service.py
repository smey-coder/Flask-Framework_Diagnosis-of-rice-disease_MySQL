from typing import Dict, Any, List
from app.models.farm import FarmTable
from extensions import db
from app.models.harvest import Harvest
from app.models.field_crop import FieldCropTable
from app.models.field import FieldTable

class HarvestService:

    @staticmethod
    def calculate_and_save_harvest(field_crop_id: int, data: Dict[str, Any]) -> Harvest:
        currency = data.get('currency', 'USD')
        rate = float(data.get('exchange_rate', 4046.0))

        raw_price = float(data.get('price_per_ton', 0.0))
        raw_cost = float(data.get('total_cost', 0.0))
        quantity = float(data.get('quantity_tons', 0.0))

        # Currency Conversion to Base USD
        if currency == 'KHR':
            price_usd = raw_price / rate if rate > 0 else 0.0
            cost_usd = raw_cost / rate if rate > 0 else 0.0
        else:
            price_usd = raw_price
            cost_usd = raw_cost

        total_revenue = round(quantity * price_usd, 2)
        net_profit = round(total_revenue - cost_usd, 2)

        harvest = Harvest(
            field_crop_id=field_crop_id,
            harvest_date=data.get('harvest_date'),
            quantity_tons=quantity,
            quality_grade=data.get('quality_grade', 'Grade A'),
            currency=currency,
            exchange_rate=rate,
            price_per_ton=round(price_usd, 2),
            total_cost=round(cost_usd, 2),
            total_revenue=total_revenue,
            net_profit=net_profit
        )

        db.session.add(harvest)
        db.session.commit()
        return harvest

    @staticmethod
    def get_user_harvest_summary(user_id: int) -> Dict[str, Any]:
        """Retrieves all harvest records across ALL farms owned by user_id."""
        harvests = (
            Harvest.query
            .join(FieldCropTable, Harvest.field_crop_id == FieldCropTable.id)
            .join(FieldTable, FieldCropTable.field_id == FieldTable.id)
            .join(FarmTable, FieldTable.farm_id == FarmTable.id)
            .filter(FarmTable.user_id == user_id)
            .order_by(Harvest.harvest_date.desc())
            .all()
        )

        total_tons = sum(h.quantity_tons for h in harvests)
        total_revenue = sum(h.total_revenue for h in harvests)
        total_cost = sum(h.total_cost for h in harvests)
        total_profit = sum(h.net_profit for h in harvests)

        roi = round((total_profit / total_cost * 100), 2) if total_cost > 0 else 0.0

        return {
            "harvests": harvests,
            "total_tons": round(total_tons, 2),
            "total_revenue": round(total_revenue, 2),
            "total_cost": round(total_cost, 2),
            "total_profit": round(total_profit, 2),
            "roi": roi
        }

    @staticmethod
    def get_field_crop_harvests(field_crop_id: int) -> List[Harvest]:
        """Utility to get all harvest records for a specific field crop."""
        return Harvest.query.filter_by(field_crop_id=field_crop_id)\
                            .order_by(Harvest.harvest_date.desc()).all()