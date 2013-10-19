/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.antigluk.telog.flume;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import org.antigluk.telog.LogEntry;
import org.antigluk.telog.LogEventListener;
import org.antigluk.telog.stream.LogEventStream;
import org.apache.flume.Context;
import org.apache.flume.Event;
import org.apache.flume.EventDrivenSource;
import org.apache.flume.channel.ChannelProcessor;
import org.apache.flume.conf.Configurable;
import org.apache.flume.event.EventBuilder;
import org.apache.flume.source.AbstractSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A Flume Source of CDR Logs
 */
public abstract class TelcoLogFlumeSource extends AbstractSource
        implements EventDrivenSource, Configurable {
    //
    private static final Logger logger =
            LoggerFactory.getLogger(TelcoLogFlumeSource.class);

    /**
     * The actual CDR stream
     */
    private final LogEventStream logEventStream;

    protected abstract LogEventStream makeLogEventStream();

    public TelcoLogFlumeSource() {
        this.logEventStream = makeLogEventStream();
    }

    /**
     * The initialization method for the Source. The context contains all the
     * Flume configuration info, and can be used to retrieve any configuration
     * values necessary to set up the Source.
     */
    @Override
    public void configure(Context context) {
        //
    }

    /**
     * Start processing events
     */
    @Override
    public void start() {
        final ChannelProcessor channel = getChannelProcessor();
        final Map<String, String> headers = new HashMap<String, String>();

        LogEventListener listener = new LogEventListener() {
            public void onMessage(LogEntry entry) {
                headers.put("timestamp", String.valueOf(entry.getTimestamp()));
                try {
                    Event event = EventBuilder.withBody(entry.toJSONString().getBytes(), headers);
                    channel.processEvent(event);
                } catch (IOException e) {
                    e.printStackTrace();
                    logger.error(e.toString());
                }
            }
        };
        logger.debug("Setting up Source to stream");

        logEventStream.addListener(listener);

        logEventStream.start();
        super.start();
    }

    /**
     * Stops the Source's event processing and shuts down the stream.
     */
    @Override
    public void stop() {
        logger.debug("Shutting down stream...");
        logEventStream.stop();
        super.stop();
    }
}
