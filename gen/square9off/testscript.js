TIMEOUT(500000);
var rad = 9;
var factor = 2.0;
var msgs = Math.ceil(factor * rad * 2);

timeout_function = function () {
    log.log("Script timed out.\n");
    log.testOK();
}

YIELD_THEN_WAIT_UNTIL(msg.contains("request "+msgs));
GENERATE_MSG(500, "script timeout");
YIELD_THEN_WAIT_UNTIL(msg.equals("script timeout"));
SCRIPT_TIMEOUT();
