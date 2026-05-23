package service.commands;

import exception.WarehouseException;

public interface WarehouseCommand {
    void execute() throws WarehouseException;

    void undo() throws WarehouseException;
}

