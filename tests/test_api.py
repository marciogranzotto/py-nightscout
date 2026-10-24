import pytest
import py_nightscout as nightscout
import json
from datetime import datetime
from dateutil.tz import tzutc
import dateutil.parser
from aioresponses import aioresponses
import pytz


@pytest.fixture(name="api")
def api_fixture() -> nightscout.Api:
    """Creates Api fixture."""
    return nightscout.Api("http://testns.example.com")


sgv_response = json.loads(
    '[{"_id":"5f2b01f5c3d0ac7c4090e223","device":"xDrip-LimiTTer","date":1596654066533,"dateString":"2020-08-05T19:01:06.533Z","sgv":169,"delta":-5.257,"direction":"FortyFiveDown","type":"sgv","filtered":182823.5157,"unfiltered":182823.5157,"rssi":100,"noise":1,"sysTime":"2020-08-05T19:01:06.533Z","utcOffset":-180},{"_id":"5f2b00c8c3d0ac7c4090e222","device":"xDrip-LimiTTer","date":1596653766048,"dateString":"2020-08-05T18:56:06.048Z","sgv":174,"delta":-2.028,"direction":"Flat","type":"sgv","filtered":187411.75065,"unfiltered":187411.75065,"rssi":100,"noise":1,"sysTime":"2020-08-05T18:56:06.048Z","utcOffset":-180},{"_id":"5f2aff9dc3d0ac7c4090e221","device":"xDrip-LimiTTer","date":1596653466421,"dateString":"2020-08-05T18:51:06.421Z","sgv":176,"delta":-5.66,"direction":"FortyFiveDown","type":"sgv","filtered":189176.4564,"unfiltered":189176.4564,"rssi":100,"noise":1,"sysTime":"2020-08-05T18:51:06.421Z","utcOffset":-180},{"_id":"5f2afe70c3d0ac7c4090e220","device":"xDrip-LimiTTer","date":1596653165840,"dateString":"2020-08-05T18:46:05.840Z","sgv":182,"delta":-2.97,"direction":"Flat","type":"sgv","filtered":194117.63249999998,"unfiltered":194117.63249999998,"rssi":100,"noise":1,"sysTime":"2020-08-05T18:46:05.840Z","utcOffset":-180},{"_id":"5f2afd44c3d0ac7c4090e21f","device":"xDrip-LimiTTer","date":1596652865845,"dateString":"2020-08-05T18:41:05.845Z","sgv":185,"delta":-5.946,"direction":"FortyFiveDown","type":"sgv","filtered":196705.8676,"unfiltered":196705.8676,"rssi":100,"noise":1,"sysTime":"2020-08-05T18:41:05.845Z","utcOffset":-180},{"_id":"5f2afc18c3d0ac7c4090e21e","device":"xDrip-LimiTTer","date":1596652566127,"dateString":"2020-08-05T18:36:06.127Z","sgv":191,"delta":-5.772,"direction":"FortyFiveDown","type":"sgv","filtered":201882.33779999998,"unfiltered":201882.33779999998,"rssi":100,"noise":1,"sysTime":"2020-08-05T18:36:06.127Z","utcOffset":-180},{"_id":"5f2afa42c3d0ac7c4090e21d","device":"xDrip-LimiTTer","date":1596652095925,"dateString":"2020-08-05T18:28:15.925Z","sgv":200,"delta":-3.51,"direction":"Flat","type":"sgv","filtered":209764.69014999998,"unfiltered":209764.69014999998,"rssi":100,"noise":1,"sysTime":"2020-08-05T18:28:15.925Z","utcOffset":-180},{"_id":"5f2af916c3d0ac7c4090e21c","device":"xDrip-LimiTTer","date":1596651795916,"dateString":"2020-08-05T18:23:15.916Z","sgv":203,"delta":-5.4,"direction":"FortyFiveDown","type":"sgv","filtered":212823.51345,"unfiltered":212823.51345,"rssi":100,"noise":1,"sysTime":"2020-08-05T18:23:15.916Z","utcOffset":-180},{"_id":"5f2af7eac3d0ac7c4090e21b","device":"xDrip-LimiTTer","date":1596651495909,"dateString":"2020-08-05T18:18:15.909Z","sgv":209,"delta":2.702,"direction":"Flat","type":"sgv","filtered":217529.39544999998,"unfiltered":217529.39544999998,"rssi":100,"noise":1,"sysTime":"2020-08-05T18:18:15.909Z","utcOffset":-180},{"_id":"5f2af6bec3d0ac7c4090e21a","device":"xDrip-LimiTTer","date":1596651196104,"dateString":"2020-08-05T18:13:16.104Z","sgv":206,"delta":-4.454,"direction":"Flat","type":"sgv","filtered":215176.45445,"unfiltered":215176.45445,"rssi":100,"noise":1,"sysTime":"2020-08-05T18:13:16.104Z","utcOffset":-180}]'
)
treatments_response = json.loads(
    '[{"_id":"58be816483ab6d6632419686","temp":"absolute","enteredBy":"loop://Riley\'s iphone","eventType":"Temp Basal","created_at":"2017-03-07T09:38:35Z","timestamp":"2017-03-07T09:38:35Z","absolute":0.7,"rate":0.7,"duration":30,"carbs":null,"insulin":null},{"_id":"58be803d83ab6d6632419683","temp":"absolute","enteredBy":"loop://Riley\'s iphone","eventType":"Temp Basal","created_at":"2017-03-07T09:33:30Z","timestamp":"2017-03-07T09:33:30Z","absolute":1.675,"rate":1.675,"duration":30,"carbs":null,"insulin":null},{"_id":"58be7f0d83ab6d6632419680","temp":"absolute","enteredBy":"loop://Riley\'s iphone","eventType":"Temp Basal","created_at":"2017-03-07T09:28:30Z","timestamp":"2017-03-07T09:28:30Z","absolute":1.775,"rate":1.775,"duration":30,"carbs":null,"insulin":null}]'
)
profile_response = json.loads(
    '[{"_id":"58c0e02447d5af0c00e37593","defaultProfile":"Default","store":{"Default":{"dia":"4","carbratio":[{"time":"00:00","value":"20","timeAsSeconds":"0"},{"time":"06:00","value":"10","timeAsSeconds":"21600"},{"time":"11:00","value":"18","timeAsSeconds":"39600"},{"time":"16:00","value":"12","timeAsSeconds":"57600"},{"time":"21:00","value":"18","timeAsSeconds":"75600"}],"carbs_hr":"20","delay":"20","sens":[{"time":"00:00","value":"90","timeAsSeconds":"0"},{"time":"06:00","value":"85","timeAsSeconds":"21600"},{"time":"09:00","value":"95","timeAsSeconds":"32400"}],"timezone":"US/Central","basal":[{"time":"00:00","value":"0.45","timeAsSeconds":"0"},{"time":"02:00","value":"0.3","timeAsSeconds":"7200"},{"time":"04:30","value":"0.45","timeAsSeconds":"16200"},{"time":"07:00","value":"0.6","timeAsSeconds":"25200"},{"time":"10:00","value":"0.4","timeAsSeconds":"36000"},{"time":"12:00","value":"0.4","timeAsSeconds":"43200"},{"time":"15:00","value":"0.4","timeAsSeconds":"54000"},{"time":"17:00","value":"0.4","timeAsSeconds":"61200"},{"time":"20:30","value":"0.4","timeAsSeconds":"73800"}],"target_low":[{"time":"00:00","value":"110","timeAsSeconds":"0"}],"target_high":[{"time":"00:00","value":"130","timeAsSeconds":"0"}],"startDate":"1970-01-01T00:00:00.000Z","units":"mg/dl"},"Test2":{"dia":"4","carbratio":[{"time":"00:00","value":"20","timeAsSeconds":"0"},{"time":"06:00","value":"10","timeAsSeconds":"21600"},{"time":"11:00","value":"18","timeAsSeconds":"39600"},{"time":"16:00","value":"12","timeAsSeconds":"57600"},{"time":"21:00","value":"18","timeAsSeconds":"75600"}],"carbs_hr":"20","delay":"20","sens":[{"time":"00:00","value":"90","timeAsSeconds":"0"},{"time":"06:00","value":"85","timeAsSeconds":"21600"},{"time":"09:00","value":"95","timeAsSeconds":"32400"}],"timezone":"US/Central","basal":[{"time":"00:00","value":"0.45","timeAsSeconds":"0"},{"time":"02:00","value":"0.3","timeAsSeconds":"7200"},{"time":"04:30","value":"0.45","timeAsSeconds":"16200"},{"time":"07:00","value":"0.6","timeAsSeconds":"25200"},{"time":"10:00","value":"0.4","timeAsSeconds":"36000"},{"time":"12:00","value":"0.4","timeAsSeconds":"43200"},{"time":"15:00","value":"0.4","timeAsSeconds":"54000"},{"time":"17:00","value":"0.4","timeAsSeconds":"61200"},{"time":"20:30","value":"0.4","timeAsSeconds":"73800"}],"target_low":[{"time":"00:00","value":"110","timeAsSeconds":"0"}],"target_high":[{"time":"00:00","value":"130","timeAsSeconds":"0"}],"startDate":"1970-01-01T00:00:00.000Z","units":"mg/dl"}},"startDate":"2017-03-24T03:54:00.000Z","mills":"1489035240000","units":"mg/dl","created_at":"2016-10-31T12:58:43.800Z"},{"_id":"58b7777cdfb94b0c00366c7e","defaultProfile":"Default","store":{"Default":{"dia":"4","carbratio":[{"time":"00:00","value":"20","timeAsSeconds":"0"},{"time":"06:00","value":"10","timeAsSeconds":"21600"},{"time":"11:00","value":"18","timeAsSeconds":"39600"},{"time":"16:00","value":"12","timeAsSeconds":"57600"},{"time":"21:00","value":"18","timeAsSeconds":"75600"}],"carbs_hr":"20","delay":"20","sens":[{"time":"00:00","value":"90","timeAsSeconds":"0"},{"time":"06:00","value":"85","timeAsSeconds":"21600"},{"time":"09:00","value":"95","timeAsSeconds":"32400"}],"timezone":"US/Central","basal":[{"time":"00:00","value":"0.45","timeAsSeconds":"0"},{"time":"02:00","value":"0.3","timeAsSeconds":"7200"},{"time":"04:30","value":"0.45","timeAsSeconds":"16200"},{"time":"07:00","value":"0.6","timeAsSeconds":"25200"},{"time":"10:00","value":"0.4","timeAsSeconds":"36000"},{"time":"12:00","value":"0.4","timeAsSeconds":"43200"},{"time":"15:00","value":"0.4","timeAsSeconds":"54000"},{"time":"17:00","value":"0.6","timeAsSeconds":"61200"},{"time":"20:30","value":"0.6","timeAsSeconds":"73800"}],"target_low":[{"time":"00:00","value":"110","timeAsSeconds":"0"}],"target_high":[{"time":"00:00","value":"130","timeAsSeconds":"0"}],"startDate":"1970-01-01T00:00:00.000Z","units":"mg/dl"}},"startDate":"2017-03-02T01:37:00.000Z","mills":"1488418620000","units":"mg/dl","created_at":"2016-10-31T12:58:43.800Z"},{"_id":"5719b2aa5c3e080b000dbfb1","defaultProfile":"Default","store":{"Default":{"dia":"4","carbratio":[{"time":"00:00","value":"18","timeAsSeconds":"0"},{"time":"06:00","value":"10","timeAsSeconds":"21600"},{"time":"11:00","value":"18","timeAsSeconds":"39600"},{"time":"16:00","value":"12","timeAsSeconds":"57600"},{"time":"21:00","value":"18","timeAsSeconds":"75600"}],"carbs_hr":"20","delay":"20","sens":[{"time":"00:00","value":"90","timeAsSeconds":"0"},{"time":"06:00","value":"85","timeAsSeconds":"21600"},{"time":"09:00","value":"95","timeAsSeconds":"32400"}],"timezone":"US/Central","basal":[{"time":"00:00","value":"0.45","timeAsSeconds":"0"},{"time":"02:00","value":"0.3","timeAsSeconds":"7200"},{"time":"04:30","value":"0.45","timeAsSeconds":"16200"},{"time":"07:00","value":"0.6","timeAsSeconds":"25200"},{"time":"10:00","value":"0.4","timeAsSeconds":"36000"},{"time":"12:00","value":"0.4","timeAsSeconds":"43200"},{"time":"15:00","value":"0.4","timeAsSeconds":"54000"},{"time":"17:00","value":"0.6","timeAsSeconds":"61200"},{"time":"20:30","value":"0.6","timeAsSeconds":"73800"}],"target_low":[{"time":"00:00","value":"110","timeAsSeconds":"0"}],"target_high":[{"time":"00:00","value":"130","timeAsSeconds":"0"}],"startDate":"1970-01-01T00:00:00.000Z","units":"mg/dl"}},"startDate":"2016-04-22T05:06:00.000Z","mills":"1461301560000","units":"mg/dl","created_at":"2016-10-31T12:58:43.800Z"}]'
)
server_status_response = json.loads(
    '{"status":"ok","name":"nightscout","version":"13.0.1","serverTime":"2020-08-05T18:14:02.032Z","serverTimeEpoch":1596651242032,"apiEnabled":true,"careportalEnabled":true,"boluscalcEnabled":true,"settings":{"units":"mg/dl","timeFormat":12,"nightMode":false,"editMode":true,"showRawbg":"never","customTitle":"Nightscout","theme":"default","alarmUrgentHigh":true,"alarmUrgentHighMins":[30,60,90,120],"alarmHigh":true,"alarmHighMins":[30,60,90,120],"alarmLow":true,"alarmLowMins":[15,30,45,60],"alarmUrgentLow":true,"alarmUrgentLowMins":[15,30,45],"alarmUrgentMins":[30,60,90,120],"alarmWarnMins":[30,60,90,120],"alarmTimeagoWarn":true,"alarmTimeagoWarnMins":15,"alarmTimeagoUrgent":true,"alarmTimeagoUrgentMins":30,"alarmPumpBatteryLow":false,"language":"en","scaleY":"log","showPlugins":" delta direction upbat","showForecast":"ar2","focusHours":3,"heartbeat":60,"baseURL":"","authDefaultRoles":"readable","thresholds":{"bgHigh":260,"bgTargetTop":180,"bgTargetBottom":80,"bgLow":55},"insecureUseHttp":false,"secureHstsHeader":true,"secureHstsHeaderIncludeSubdomains":false,"secureHstsHeaderPreload":false,"secureCsp":false,"deNormalizeDates":false,"showClockDelta":false,"showClockLastTime":false,"DEFAULT_FEATURES":["bgnow","delta","direction","timeago","devicestatus","upbat","errorcodes","profile"],"alarmTypes":["predict"],"enable":["careportal","boluscalc","food","bwp","cage","sage","iage","iob","cob","basal","ar2","rawbg","pushover","bgi","pump","openaps","treatmentnotify","bgnow","delta","direction","timeago","devicestatus","upbat","errorcodes","profile","ar2"]},"extendedSettings":{"devicestatus":{"advanced":true}},"authorized":null}'
)
device_status_response = json.loads(
    '[{"_id":"617dc8ef0c76ce0182e37978","device":"Tomato","uploader":{"battery":20,"type":"BRIDGE"},"created_at":"2021-10-30T22:36:31.901Z","utcOffset":-180,"mills":1635633391901},{"_id":"617dc8ef0c76ce0182e37977","device":"samsung SM-N986B","uploader":{"battery":69,"type":"PHONE"},"created_at":"2021-10-30T22:36:31.844Z","utcOffset":-180,"mills":1635633391844},{"_id":"617dc7c40c76ce0182e37976","device":"Tomato","uploader":{"battery":20,"type":"BRIDGE"},"created_at":"2021-10-30T22:31:32.252Z","utcOffset":-180,"mills":1635633092252},{"_id":"617dc7c40c76ce0182e37975","device":"samsung SM-N986B","uploader":{"battery":70,"type":"PHONE"},"created_at":"2021-10-30T22:31:32.198Z","utcOffset":-180,"mills":1635633092198},{"_id":"617dc6980c76ce0182e37974","device":"Tomato","uploader":{"battery":20,"type":"BRIDGE"},"created_at":"2021-10-30T22:26:32.128Z","utcOffset":-180,"mills":1635632792128},{"_id":"617dc6980c76ce0182e37973","device":"samsung SM-N986B","uploader":{"battery":70,"type":"PHONE"},"created_at":"2021-10-30T22:26:32.043Z","utcOffset":-180,"mills":1635632792043},{"_id":"617dc56c0c76ce0182e37972","device":"Tomato","uploader":{"battery":20,"type":"BRIDGE"},"created_at":"2021-10-30T22:21:32.955Z","utcOffset":-180,"mills":1635632492955},{"_id":"617dc56c0c76ce0182e37971","device":"samsung SM-N986B","uploader":{"battery":70,"type":"PHONE"},"created_at":"2021-10-30T22:21:32.902Z","utcOffset":-180,"mills":1635632492902},{"_id":"617dc43f0c76ce0182e37970","device":"Tomato","uploader":{"battery":20,"type":"BRIDGE"},"created_at":"2021-10-30T22:16:31.839Z","utcOffset":-180,"mills":1635632191839},{"_id":"617dc43f0c76ce0182e3796f","device":"samsung SM-N986B","uploader":{"battery":70,"type":"PHONE"},"created_at":"2021-10-30T22:16:31.784Z","utcOffset":-180,"mills":1635632191784}]'
)


@pytest.mark.asyncio
async def test_get_sgv(api: nightscout.Api):
    """Tests using external session."""
    with aioresponses() as response:
        response.get(
            "http://testns.example.com/api/v1/entries/sgv.json",
            payload=sgv_response,
        )
        entries = await api.get_sgvs()
        assert 10 == len(entries)
        assert 169 == entries[0].sgv
        assert 9.4 == entries[0].sgv_mmol
        assert -5.257 == entries[0].delta
        assert -0.3 == entries[0].delta_mmol
        assert "FortyFiveDown" == entries[0].direction
        assert -5.257 == entries[0].delta
        assert datetime(2020, 8, 5, 19, 1, 6, 533000, tzinfo=tzutc()) == entries[0].date


@pytest.mark.asyncio
async def test_get_treatments(api: nightscout.Api):
    with aioresponses() as response:
        response.get(
            "http://testns.example.com/api/v1/treatments.json",
            payload=treatments_response,
        )

        treatments = await api.get_treatments()

        assert 3 == len(treatments)
        assert "absolute" == treatments[0].temp
        assert "Temp Basal" == treatments[0].eventType
        timestamp = datetime(2017, 3, 7, 9, 38, 35, tzinfo=tzutc())
        assert timestamp == treatments[0].timestamp
        assert timestamp == treatments[0].created_at


@pytest.mark.asyncio
async def test_get_profile(api: nightscout.Api):
    with aioresponses() as response:
        response.get(
            "http://testns.example.com/api/v1/profile.json",
            payload=profile_response,
        )

        profile_definition_set = await api.get_profiles()

        profile_definition = profile_definition_set.get_profile_definition_active_at(
            datetime(2017, 3, 5, 0, 0, tzinfo=tzutc())
        )
        assert (
            datetime(2017, 3, 2, 1, 37, tzinfo=tzutc()) == profile_definition.startDate
        )
        assert "mg/dl" == profile_definition.units

        profile = profile_definition.get_default_profile()
        assert pytz.timezone("US/Central") == profile.timezone
        assert 4 == profile.dia

        five_thirty_pm = datetime(2017, 3, 24, 17, 30)
        five_thirty_pm = profile.timezone.localize(five_thirty_pm)
        assert 0.6 == profile.basal.value_at_date(five_thirty_pm)


@pytest.mark.asyncio
async def test_server_status(api: nightscout.Api):
    with aioresponses() as response:
        response.get(
            "http://testns.example.com/api/v1/status.json",
            payload=server_status_response,
        )

        server_status = await api.get_server_status()

        assert "ok" == server_status.status
        assert "nightscout" == server_status.name
        assert server_status.apiEnabled
        assert "readable" == server_status.settings["authDefaultRoles"]


@pytest.mark.asyncio
async def test_devices_status(api: nightscout.Api):
    with aioresponses() as response:
        response.get(
            "http://testns.example.com/api/v1/devicestatus.json",
            payload=device_status_response,
        )

        devices_status = await api.get_devices_status()

        assert 10 == len(devices_status)
        assert "Tomato" == devices_status[0].device
        assert 20 == devices_status[0].uploader.battery


@pytest.mark.asyncio
async def test_latest_devices_status(api: nightscout.Api):
    with aioresponses() as response:
        response.get(
            "http://testns.example.com/api/v1/devicestatus.json",
            payload=device_status_response,
        )

        devices_status = await api.get_latest_devices_status()

        assert 2 == len(devices_status)
        assert devices_status["Tomato"]
        assert devices_status["samsung SM-N986B"]
        assert (
            dateutil.parser.parse("2021-10-30T22:36:31.901Z")
            == devices_status["Tomato"].created_at
        )
        assert 20 == devices_status["Tomato"].uploader.battery
        assert "BRIDGE" == devices_status["Tomato"].uploader.type
        assert (
            dateutil.parser.parse("2021-10-30T22:36:31.844Z")
            == devices_status["samsung SM-N986B"].created_at
        )
        assert 69 == devices_status["samsung SM-N986B"].uploader.battery
        assert "PHONE" == devices_status["samsung SM-N986B"].uploader.type


@pytest.mark.asyncio
async def test_post_treatments(api: nightscout.Api):
    treatment = {
        "eventType": "Meal Bolus",
        "carbs": 30,
        "enteredBy": "py-nightscout",
        "created_at": "2017-03-07T09:38:35Z",
    }
    note = {
        "eventType": "Note",
        "notes": "Pizza",
        "enteredBy": "py-nightscout",
        "created_at": "2017-03-07T09:40:00Z",
    }
    with aioresponses() as response:
        response.post(
            "http://testns.example.com/api/v1/treatments",
            payload=[
                {"_id": "58be816483ab6d6632419690", **treatment},
                {"_id": "58be816483ab6d6632419691", **note},
            ],
        )
        treatments = await api.post_treatments([treatment, note])
        assert 2 == len(treatments)
        assert "Meal Bolus" == treatments[0].eventType
        assert 30 == treatments[0].carbs
        assert "Pizza" == treatments[1].notes
        timestamp = datetime(2017, 3, 7, 9, 38, 35, tzinfo=tzutc())
        assert timestamp == treatments[0].created_at
        request = list(response.requests.values())[0][0]
        assert [treatment, note] == request.kwargs["json"]


@pytest.mark.asyncio
async def test_post_treatment_with_secret():
    api = nightscout.Api("http://testns.example.com", api_secret="secret")
    treatment = {"eventType": "Correction Bolus", "insulin": 1.5}
    with aioresponses() as response:
        response.post(
            "http://testns.example.com/api/v1/treatments",
            payload=[{"_id": "58be816483ab6d6632419692", **treatment}],
        )
        result = await api.post_treatment(treatment)
        assert "Correction Bolus" == result.eventType
        assert 1.5 == result.insulin
        request = list(response.requests.values())[0][0]
        assert (
            "e5e9fa1ba31ecd1ae84f75caaa474f3a663f05f4"
            == request.kwargs["headers"]["api-secret"]
        )


@pytest.mark.asyncio
async def test_post_treatment_error(api: nightscout.Api):
    from aiohttp import ClientResponseError

    with aioresponses() as response:
        response.post("http://testns.example.com/api/v1/treatments", status=401)
        with pytest.raises(ClientResponseError):
            await api.post_treatment({"eventType": "Note"})


def test_treatment_insulin_injections():
    raw = '[{"insulin": "Humalog", "units": 5}]'
    t = nightscout.Treatment(eventType="Correction Bolus", insulin=5, insulinInjections=raw)
    assert t.insulinInjections == raw
    assert nightscout.Treatment(eventType="Note").insulinInjections is None
