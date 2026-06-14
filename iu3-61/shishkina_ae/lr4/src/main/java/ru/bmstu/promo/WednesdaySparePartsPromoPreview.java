package ru.bmstu.promo;

import ru.bmstu.model.OrderPart;
import ru.bmstu.model.RepairOrder;


public final class WednesdaySparePartsPromoPreview {


    public static String buildPromoHintForOrder(RepairOrder order) {
        int day = java.time.LocalDate.now().getDayOfWeek().getValue();
        if (day != 3) {
            return "Акция не действует сегодня (условие: только среда)";
        }

        double sparePartsAfterPromo = 0.0;
        double sparePartsBaseline = 0.0;

        for (OrderPart line : order.getUsedParts()) {
            double lineCost = line.calculateCost();
            sparePartsBaseline += lineCost;

            if (line.getPart().getPrice() >= 300) {
                sparePartsAfterPromo += lineCost * 0.85;
            } else {
                sparePartsAfterPromo += lineCost;
            }
        }

        return "Предпросмотр акции скидка 15% на запчасти с ценой больше 300 за штуку в среду»: "
                + "Стоимость без скидки: " + sparePartsBaseline
                + ", с учётом скидки " + sparePartsAfterPromo;
    }
}
