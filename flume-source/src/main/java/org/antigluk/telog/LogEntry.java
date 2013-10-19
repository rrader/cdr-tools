package org.antigluk.telog;

import org.json.simple.JSONObject;

import java.io.IOException;
import java.io.StringWriter;
import java.util.Date;

public abstract class LogEntry {
    protected Date timestamp;

    public LogEntry(Date timestamp) {
        this.timestamp = timestamp;
    }

    public void setTimestamp(Date timestamp) {
        this.timestamp = timestamp;
    }

    public Date getTimestamp() {

        return timestamp;
    }

    public abstract JSONObject toJSON();

    public String toJSONString() throws IOException {
        StringWriter out = new StringWriter();
        this.toJSON().writeJSONString(out);
        String jsonText = out.toString();
        return jsonText;
    }
}
