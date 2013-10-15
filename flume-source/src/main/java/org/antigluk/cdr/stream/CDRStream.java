package org.antigluk.cdr.stream;

import org.antigluk.cdr.CDRListener;

public interface CDRStream {
    public void addListener(CDRListener listener);
    public void start();
    public void stop();
}
