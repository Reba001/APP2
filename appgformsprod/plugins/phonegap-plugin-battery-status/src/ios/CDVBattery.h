/*
 Licensed to the Apache Software Foundation (ASF) under one
 or more contributor license agreements.  See the NOTICE file
 distributed with this work for additional information
 regarding copyright ownership.  The ASF licenses this file
 to you under the Apache License, Version 2.0 (the
 "License"); you may not use this file except in compliance
 with the License.  You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing,
 software distributed under the License is distributed on an
 "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 KIND, either express or implied.  See the License for the
 specific language governing permissions and limitations
 under the License.
 */

#import <Foundation/Foundation.h>
#import <Cordova/CDVPlugin.h>

@interface CDVBattery : CDVPlugin {
    UIDeviceBatteryState state;
    float level;
    bool isPlugged;
    NSString* callbackId;
}

@property (nonatomic) UIDeviceBatteryState state;
@property (nonatomic) float level;
@property (nonatomic) bool isPlugged;
@property (nonatomic) NSDictionary* getBattery;
@property (strong) NSString* callbackId;

- (void)updateBatteryStatus:(NSNotification*)notification;
- (void)getBatteryStatus:(CDVInvokedUrlCommand*)command;

@end
