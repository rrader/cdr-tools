package org.antigluk.telog.stream;

import org.antigluk.telog.LogEventListener;

public interface LogEventStream {
    public void addListener(LogEventListener listener);
    public void start();
    public void stop();
}
