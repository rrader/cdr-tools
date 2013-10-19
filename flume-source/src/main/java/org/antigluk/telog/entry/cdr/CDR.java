package org.antigluk.telog.entry.cdr;

import org.antigluk.telog.LogEntry;
import org.json.simple.JSONObject;

import java.util.Date;

public class CDR extends LogEntry {
    private String from_number;
    private String to_number;
    private Status status;
    private Date start_time;
    private int duration;

    public void setFrom_number(String from_number) {
        this.from_number = from_number;
    }

    public void setTo_number(String to_number) {
        this.to_number = to_number;
    }

    public void setStatus(Status status) {
        this.status = status;
    }

    public void setStart_time(Date start_time) {
        this.start_time = start_time;
    }

    public void setDuration(int duration) {
        this.duration = duration;
    }

    public String getFrom_number() {

        return from_number;
    }

    public String getTo_number() {
        return to_number;
    }

    public Status getStatus() {
        return status;
    }

    public Date getStart_time() {
        return start_time;
    }

    public int getDuration() {
        return duration;
    }

    public CDR(Date timestamp, String from_number, String to_number, Status status, Date start_time, int duration) {
        super(timestamp);
        this.from_number = from_number;
        this.to_number = to_number;
        this.status = status;
        this.start_time = start_time;
        this.duration = duration;
    }

    @Override
    public JSONObject toJSON() {
        JSONObject obj=new JSONObject();
        obj.put("from", this.from_number);
        obj.put("to", this.to_number);
        obj.put("status", new Integer(this.status.ordinal()));
        obj.put("start", this.start_time);
        obj.put("duration", new Integer(this.duration));
        return obj;
    }

}
