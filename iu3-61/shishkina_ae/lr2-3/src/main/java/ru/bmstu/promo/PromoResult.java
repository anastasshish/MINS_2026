package ru.bmstu.promo;

public record PromoResult(boolean applied, double baselineCost, double finalCost, String message) {

    public String toHint() {
        if (!applied) {
            return message;
        }
        return message
                + " Стоимость без скидки: " + baselineCost
                + ", с учётом скидки: " + finalCost;
    }
}
