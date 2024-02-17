{% args infos %}
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta content='width=device-width, initial-scale=1, maximum-scale=1' name='viewport'>
    <title>{{ infos['device_description'] }}</title></head>
<style>* {
    font-family: -apple-system, BlinkMacSystemFont, segoe ui, Tahoma, pingfang sc, hiragino sans gb, microsoft yahei, sans-serif, simsun;
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none
}

body {
    background: #f3f3f8;
    margin: 0 auto
}

.header {
    padding-top: 20px;
    text-align: center
}

.header span {
    font-size: 30px;
    font-weight: 600
}

.setup, .about {
    background: #fff;
    margin: 0 auto;
    border-top: .5px solid #cacacc;
    border-bottom: .5px solid #cacacc;
    position: relative;
    overflow: hidden
}

.setup nav {
    height: 45px;
    line-height: 45px;
    padding: 0 15px;
    cursor: pointer;
    font-size: 14px
}

.setup nav span, .about nav span {
    float: right;
    color: #8a8a8d
}

.setup nav:after, .about nav:after {
    content: "";
    height: .5px;
    background: #cacacc;
    width: 100%;
    left: 15px;
    position: absolute;
    margin-top: 45px
}

.setup nav:active {
    background: #9e9e9e
}

.setup nav:last-child:after {
    display: none
}

.about nav {
    height: 45px;
    line-height: 45px;
    padding: 0 15px;
    font-size: 14px
}

.notice {
    margin: 10px auto;
    color: #6d6d71;
    font-size: 12px;
    text-align: left;
    margin-left: 15px
}

.title {
    color: #000;
    font-size: 20px;
    margin: 20px auto;
    text-align: center
}

.clickable {
    color: #336EFF;
}

.power {
    text-align: center
}

.footer {
    margin-top: 20px;
    margin-bottom: 20px;
    color: #eb4d3d !important;
    text-align: center
}

@media (prefers-color-scheme: dark) {
    body {
        background: #000;
        color: #fff
    }

    .setup, .about {
        background: #1c1c1d;
        border-color: #3b3b3e;
        color: #fff
    }

    .setup nav:after, .about nav:after {
        background: #3b3b3e
    }

    .title, .notice {
        color: #98989e
    }
}

@media screen and (min-width: 700px) {
    .title, .notice {
        margin: 15px auto
    }

    .notice {
        margin-bottom: 25px;
        margin-left: 15px
    }

    .setup, .about {
        margin: 10px auto;
        border-radius: 15px;
        border: 0
    }
}

@media screen and (min-width: 1000px) {
    body {
        width: 600px;
        margin: 0 auto
    }
}</style>
<body>
<div class='header'><span>{{ infos['device_description'] }}</span></div>
<div class=title>Settings</div>
<div class=setup>
    <nav class=clickable onclick=window.location.href='/machine/reset'>Reboot the device</nav>
    <nav class=clickable onclick=window.location.href='/stats/reset'>Reset DeviceInfo Statistics</nav>
    <nav class=clickable onclick=window.location.href='/config'>Download Config (Backup)</nav>
</div>
<div class=notice>Note: For security reasons the password will be excluded when downloading the config file.
</div>
<div class='title'>DeviceInfo</div>
<div class='about'>
    <nav>DeviceInfo model<span>{{ infos['device_model'] }}</span></nav>
    <nav>Firmware version<span>{{ infos['device_firmware'] }}</span></nav>
    <nav>Free memory<span>{{ infos['device_freemem'] }} kB</span></nav>
    <nav>Flash size<span>{{ infos['device_totalspace'] }} MB</span></nav>
    <nav>CPU frequency<span>{{ infos['device_cpufreq'] }} Mhz</span></nav>
    <nav>Uptime<span>{{ infos['device_uptime'] }} h</span></nav>
</div>

<div class='title'>NetworkManager</div>
<div class='about'>
    <nav>Connected to NetworkManager<span>{{ infos['network_connected'] }}</span></nav>
    <nav>SSID<span>{{ infos['network_ssid'] }}</span></nav>
    <nav>RSSI<span>nA dB</span></nav>
    <nav>Hostname<span>{{ infos['network_hostname'] }}</span></nav>
    <nav>IP<span>{{ infos['network_ip'] }}</span></nav>
    <nav>Subnet<span>{{ infos['network_subnet'] }}</span></nav>
    <nav>Gateway<span>{{ infos['network_gateway'] }}</span></nav>
    <nav>DNS<span>{{ infos['network_dns'] }}</span></nav>
    <nav>MAC address<span>{{ infos['network_mac'] }}</span></nav>
</div>

<div class='title'>Statistics</div>
<div class='about'>
    <nav>Single Grinds done<span>{{ infos['stats_grinds_single'] }}</span></nav>
    <nav>Double Grinds done<span>{{ infos['stats_grinds_double'] }}</span></nav>
    <nav>Total grinding Time<span>{{ infos['stats_grinds_total_time'] }}</span></nav>
</div>

<div class='title'>Grinder settings</div>
<div class='about'>
    <form action='/update'>
        <nav>
            Single Grind duration
            <span>
                <input type="number" id="single" name="single" required minlength="4" maxlength="4" size="4" value={{ infos['grind_single_duration'] }}>
            </span>
        </nav>
        <nav>
            Double Grind duration
            <span>
                <input type="number" id="double" name="double" required minlength="4" maxlength="4" size="4" value={{ infos['grind_double_duration'] }}>
            </span>
        </nav>
        <nav>Grind memorize timeout
            <span>
                <input type="number" id="timeout" name="timeout" required minlength="4" maxlength="4" size="4" value={{ infos['grind_memorize_timeout'] }}>
            </span>
        </nav>

        <nav>
            <input type="submit" value="Save">
        </nav>
    </form>

</div>

<div class="setup footer">
    <nav onclick=window.location.href='https://github.com/pburkhalter'>Created with ♥ by Patrik Burkhalter</nav>
</div>

</body>



