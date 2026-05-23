package service.commands;

import exception.WarehouseException;

import java.util.ArrayDeque;
import java.util.Deque;

public class CommandExecutor {

    private final Deque<WarehouseCommand> history = new ArrayDeque<>();

    public void execute(WarehouseCommand command) throws WarehouseException {
        if (command == null) {
            return;
        }
        command.execute();
        history.push(command);
    }

    public boolean undoLast() throws WarehouseException {
        WarehouseCommand command = history.poll();
        if (command == null) {
            return false;
        }
        command.undo();
        return true;
    }
}

