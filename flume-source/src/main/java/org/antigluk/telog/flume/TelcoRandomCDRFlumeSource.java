package org.antigluk.telog.flume;

import org.antigluk.telog.stream.CDRRandomStream;
import org.antigluk.telog.stream.LogEventStream;

public class TelcoRandomCDRFlumeSource extends TelcoLogFlumeSource {
    @Override
    protected LogEventStream makeLogEventStream() {
        return new CDRRandomStream();
    }
}
