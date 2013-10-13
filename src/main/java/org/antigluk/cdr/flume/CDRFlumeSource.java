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

package org.antigluk.cdr.flume;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import org.antigluk.cdr.CDR;
import org.antigluk.cdr.CDRListener;
import org.antigluk.cdr.stream.CDRRandomStream;
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
public class CDRFlumeSource extends AbstractSource
        implements EventDrivenSource, Configurable {
    //
    private static final Logger logger =
            LoggerFactory.getLogger(CDRFlumeSource.class);

    /**
     * The actual CDR stream
     */
    private final CDRRandomStream cdrStream = new CDRRandomStream();

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

        CDRListener listener = new CDRListener() {
            public void onMessage(CDR cdr) {
                logger.debug(cdr.getFrom_number() + " -> " + cdr.getTo_number());

                headers.put("timestamp", String.valueOf(cdr.getStart_time()));
                try {
                    Event event = EventBuilder.withBody(cdr.toJSONString().getBytes(), headers);
                    channel.processEvent(event);
                } catch (IOException e) {
                    e.printStackTrace();
                    logger.error(e.toString());
                }
            }
        };
        logger.debug("Setting up CDR Source to stream");

        cdrStream.addListener(listener);

        cdrStream.start();
        super.start();
    }

    /**
     * Stops the Source's event processing and shuts down the stream.
     */
    @Override
    public void stop() {
        logger.debug("Shutting down CDR stream...");
        cdrStream.stop();
        super.stop();
    }
}
