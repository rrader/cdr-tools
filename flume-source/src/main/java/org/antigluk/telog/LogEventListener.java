package org.antigluk.telog;

public interface LogEventListener {
    void onMessage(LogEntry entry);
}
