package ui;

import model.Product;
import model.ProductCategory;
import model.StorageCell;
import repository.CellRepository;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class WarehouseAuditGodClass {
    //Дубляж - уже есть в проекте
    private static final int NEIGHBORHOOD_RADIUS = 5;

    private final CellRepository repository;

    public WarehouseAuditGodClass(CellRepository repository) {
        this.repository = repository;
    }

    public void runAudit() {
        List<StorageCell> cells = repository.findAllCells();
        System.out.println("\n=== AUDIT: склад ===");

        if (cells == null || cells.isEmpty()) {
            System.out.println("Склад пуст. Проблем не найдено.");
            return;
        }

        int totalUnits = 0;
        for (StorageCell c : cells) {
            if (c != null && c.product() != null) {
                totalUnits += c.product().getQuantity();
            }
        }

        System.out.println("Ячеек занято: " + cells.size());
        System.out.println("Всего единиц товара: " + totalUnits);

        List<String> issues = new ArrayList<>();

        for (StorageCell cell : cells) {
            if (cell == null) {
                issues.add("Найден null StorageCell (данные повреждены)");
                continue;
            }
            Product p = cell.product();
            if (p == null) {
                issues.add("Ячейка " + cell.position() + " содержит null товар (данные повреждены)");
                continue;
            }
            if (p.getId() == null || p.getId().trim().isEmpty()) {
                issues.add("Пустой ID у товара в ячейке " + cell.position());
            }
            if (p.getName() == null || p.getName().trim().isEmpty()) {
                issues.add("Пустое название у товара " + safe(p.getId()) + " в ячейке " + cell.position());
            }
            if (p.getQuantity() < 0) {
                issues.add("Отрицательное количество у товара " + safe(p.getId()) + " в ячейке " + cell.position() + ": " + p.getQuantity());
            }
        }

        int minPos = Integer.MAX_VALUE;
        int maxPos = Integer.MIN_VALUE;
        Set<Integer> occupied = new HashSet<>();
        for (StorageCell cell : cells) {
            if (cell == null) continue;
            occupied.add(cell.position());
            if (cell.position() < minPos) minPos = cell.position();
            if (cell.position() > maxPos) maxPos = cell.position();
        }
        if (minPos != Integer.MAX_VALUE && maxPos != Integer.MIN_VALUE) {
            int holes = 0;
            for (int p = minPos; p <= maxPos; p++) {
                if (!occupied.contains(p)) holes++;
            }
            if (holes > 0) {
                issues.add("Пустых ячеек в диапазоне [" + minPos + ".." + maxPos + "]: " + holes);
            }
        }

        Set<String> seenConflicts = new HashSet<>();
        for (StorageCell cell : cells) {
            if (cell == null || cell.product() == null) continue;
            int pos = cell.position();
            Product center = cell.product();
            List<Product> near = repository.findProductsInRange(pos, NEIGHBORHOOD_RADIUS);
            if (near == null || near.isEmpty()) continue;

            for (Product other : near) {
                if (other == null) continue;
                if (other.getId() != null && other.getId().equals(center.getId())) continue;

                boolean isBadPair = (center.getCategory() == ProductCategory.FOOD && other.getCategory() == ProductCategory.CHEMICALS)
                        || (center.getCategory() == ProductCategory.CHEMICALS && other.getCategory() == ProductCategory.FOOD);
                if (!isBadPair) continue;

                String key = normalizePair(center.getId(), other.getId());
                if (seenConflicts.add(key)) {
                    issues.add("Нарушено соседство в радиусе " + NEIGHBORHOOD_RADIUS + ": " + center.getCategory()
                            + " (" + safe(center.getId()) + ") рядом с " + other.getCategory() + " (" + safe(other.getId()) + ")");
                }
            }
        }

        // итог
        if (issues.isEmpty()) {
            System.out.println("Проблем не найдено.");
            return;
        }

        System.out.println("\nПроблемы (" + issues.size() + "):");
        for (int i = 0; i < issues.size(); i++) {
            System.out.println((i + 1) + ") " + issues.get(i));
        }
    }

    private static String safe(String s) {
        return s == null ? "<null>" : s;
    }

    private static String normalizePair(String a, String b) {
        String sa = safe(a);
        String sb = safe(b);
        return sa.compareTo(sb) <= 0 ? sa + "||" + sb : sb + "||" + sa;
    }
}