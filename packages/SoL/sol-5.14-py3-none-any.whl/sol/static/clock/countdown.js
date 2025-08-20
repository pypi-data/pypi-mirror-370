// -*- coding: utf-8 -*-
// :Project:   SoL -- Show an animated countdown
// :Created:   mer 27 apr 2016 11:05:23 CEST
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2016, 2022, 2023 Lele Gaifax
//

//jsl:declare Audio
//jsl:declare clearInterval
//jsl:declare setInterval
//jsl:declare setTimeout
//jsl:declare soundManager

///////////////////
// BaseCountdown //
///////////////////

function fullHeight(el) {
  return el.offsetHeight
    + parseInt(window.getComputedStyle(el).getPropertyValue('margin-top'))
    + parseInt(window.getComputedStyle(el).getPropertyValue('margin-bottom'));
}

class BaseCountdown {
  constructor(canvasId, duration, preAlarm, elapsed) {
    const title = document.getElementById('title'),
          buttons = document.getElementById('buttons'),
          wh = window.innerHeight - fullHeight(title) - fullHeight(buttons) - 20, // empirical
          ww = window.innerWidth - 20; // empirical

    this.duration = duration;
    this.preAlarm = preAlarm;
    if(elapsed !== false && elapsed < 1000 * 60 * duration)
      this.startedAt = Date.now() - elapsed;
    else
      this.startedAt = false;

    this.size = Math.min(wh, ww);
    this.lineWidth = Math.trunc(this.size / 30);
    this.radius = Math.trunc((this.size - this.lineWidth*1.1) / 2);
    this.squareSize = Math.trunc(Math.sqrt((this.radius*2) * (this.radius*2) / 2)
                                 - this.lineWidth);
    this.fontFamily = 'arial';
    this.fontSize = Math.trunc(this.squareSize / 2) + 'px';

    this.canvas = document.getElementById(canvasId);
    this.canvas.setAttribute("width", this.size);
    this.canvas.setAttribute("height", this.size);
    this.canvas.style.width = this.size + "px";
    this.canvas.style.height = this.size + "px";

    this.ctx = this.canvas.getContext("2d");
    this.ctx.font = this.fontSize + ' ' + this.fontFamily;
    this.ctx.lineWidth = this.lineWidth;
    this.ctx.strokeStyle = 'black';
    this.ctx.textBaseline = 'middle';
    this.ctx.textAlign = 'center';

    this.stopSign = document.getElementById('stop-sign');
    this.buttons = buttons;

    this.timeLeftTextHeight = null;
  }

  computeTextHeight(text, fontSize) {
    const self = this,
          div = document.createElement("div");
    var height;

    div.innerHTML = text;
    div.style.position = 'absolute';
    div.style.top = '-10000px';
    div.style.left = '-10000px';
    div.style.fontFamily = self.fontFamily;
    div.style.fontSize = fontSize || self.fontSize;
    document.body.appendChild(div);
    height = div.offsetHeight;
    document.body.removeChild(div);

    return height;
  }

  draw() {
    const self = this,
          middle = self.size / 2,
          ctx = self.ctx;

    ctx.clearRect(0, 0, self.size, self.size);

    ctx.beginPath();
    ctx.arc(middle, middle, self.radius, 0, 2 * Math.PI);
    ctx.stroke();
  }

  updateTimeLeft(left) {
    const self = this,
          ctx = self.ctx,
          mins = Math.trunc(left),
          secs = Math.trunc((left-mins)*60),
          mtext = `${mins}'`,
          stext = `${secs}"`,
          middle = self.size / 2,
          fontSize = self.radius / 10 + 'px',
          textHeight = self.computeTextHeight('1', fontSize),
          clearRadius = self.radius * 0.9 - textHeight / 2;
    var y, oldFillStyle;

    oldFillStyle = ctx.fillStyle;
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(middle, middle, clearRadius, 0, 2 * Math.PI);
    ctx.fill();
    ctx.fillStyle = oldFillStyle;

    if(!self.timeLeftTextHeight)
      self.timeLeftTextHeight = self.computeTextHeight(mtext);

    if(mins) {
      y = middle - self.timeLeftTextHeight / 2;
      ctx.fillText(mtext, middle, y);
      y += self.timeLeftTextHeight;
    } else {
      y = middle;
    }
    ctx.fillText(stext, middle, y);
  }

  drawInterval() {
    const self = this,
          fontSize = self.radius / 10 + 'px',
          textHeight = self.computeTextHeight('1', fontSize),
          radius = self.radius * 0.9 - textHeight / 2,
          ctx = self.ctx,
          middle = self.size / 2,
          start = new Date(self.startedAt),
          stop = new Date(self.startedAt + 1000 * 60 * self.duration);

    function lpad(num) {
      return (num < 10 ? '0' : '') + num;
    };

    function textRadiants(t) {
      var angle = 0;
      for (var i = t.length-1; i >= 0; i--) {
        var cw = ctx.measureText(t[i]).width;
        angle += (cw / (radius - textHeight));
      }
      return angle;
    };

    function drawCurvedText(t, top) {
      var angle;

      ctx.save();
      ctx.font = fontSize + ' ' + self.fontFamily;
      ctx.lineCap = "round";
      ctx.lineWidth = self.lineWidth / 10;
      ctx.translate(middle, middle);

      angle = (top ? -1 : 1) * textRadiants(t) / 2;
      ctx.rotate(angle);

      for (var i = 0; i < t.length; i++) {
        var cw = ctx.measureText(t[i]).width,
            ca = cw / (radius - textHeight);
        ctx.rotate((top ? 1 : -1) * ca / 2);
        if(t[i] == '—') {
          var sep = (top ? -1 : 1) * Math.PI / 2 + (top ? 1 : -1) * angle;
          ctx.beginPath();
          ctx.arc(0, 0, radius + textHeight / 2, sep, sep + ca);
          ctx.stroke();
        } else
          ctx.fillText(t[i], 0, (top ? -1 : 1) * (radius + textHeight / 2));
        ctx.rotate((top ? 1 : -1) * ca / 2);
        angle += (top ? 1 : -1) * ca;
      }
      ctx.restore();
    };

    let text = (lpad(start.getHours())
                + ':'
                + lpad(start.getMinutes())
                + ':'
                + lpad(start.getSeconds())
                + ' — '
                + lpad(stop.getHours())
                + ':'
                + lpad(stop.getMinutes())
                + ':'
                + lpad(stop.getSeconds()));
    drawCurvedText(text, true);
  }

  stop() {
    const self = this;

    if(self.updateInterval) {
      clearInterval(self.updateInterval);
      self.updateInterval = 0;
    }
  }

  terminate() {
    const self = this,
          canvas = self.canvas,
          stopSign = self.stopSign,
          buttons = self.buttons;

    self.stop();

    canvas.classList.toggle('invisible');
    stopSign.classList.toggle('invisible');
    buttons.classList.toggle('invisible');
  }

  close() {
    const self = this;

    self.stop();
    window.close();
  }
}

//////////////////
// PreCountdown //
//////////////////

class PreCountdown extends BaseCountdown {
  constructor(canvasId, duration, preAlarm) {
    super(canvasId, duration, preAlarm, false);
    this.pre_alarm_done = false;
  }

  addMinutes(minutes) {
    const self = this;

    self.duration += minutes;
    self.pre_alarm_done = false;
    self.draw();
    self.drawInterval();
  }

  start() {
    const self = this,
          ctx = self.ctx,
          middle = self.size/2,
          radius = self.radius;

    function update() {
      const started_at = self.startedAt,
            now = Date.now(),
            total_ticks = 1000 * 60 * self.duration,
            radiants_per_tick = 2 * Math.PI / total_ticks,
            progress = now - started_at,
            pre_alarm = (self.preAlarm
                         ? started_at + 1000 * 60 * (self.duration - self.preAlarm)
                         : false),
            start = 2 * Math.PI * progress / 1000 / 60 - Math.PI / 2;

      ctx.beginPath();
      ctx.arc(middle, middle, radius, 0, 2 * Math.PI);
      ctx.stroke();

      ctx.save();
      ctx.beginPath();
      ctx.strokeStyle = !pre_alarm || now > pre_alarm ? 'red' : 'orange';
      ctx.lineWidth = self.lineWidth * 0.9;
      ctx.arc(middle, middle, radius, start, start + progress * radiants_per_tick);
      ctx.stroke();
      ctx.restore();

      if(progress < total_ticks) {
        if(!self.pre_alarm_done && pre_alarm && now > pre_alarm) {
          soundManager.play('prealarm');
          self.pre_alarm_done = true;
        }
        self.updateTimeLeft(self.duration - (progress / 1000 / 60));
      } else {
        self.stop();
        soundManager.play('stop');
        self.terminate();
      }
    };

    self.startedAt = Date.now();
    self.drawInterval();
    self.updateInterval = setInterval(update, 1000 / 20);
  }
}

///////////////
// Countdown //
///////////////

class Countdown extends BaseCountdown {
  constructor(canvasId, duration, preAlarm, elapsed, isOwner) {
    super(canvasId, duration, preAlarm, elapsed);

    this.isOwner = isOwner;

    this.updateInterval = 0;
    this.tictacting = false;
  }

  draw(noimage) {
    const self = this,
          scr = document.getElementById('scr'),
          middle = self.size / 2,
          ih = self.squareSize,
          iw = self.squareSize * (scr.width / scr.height),
          ctx = self.ctx;

    super.draw();

    if(self.startedAt)
      self.start();
    else
      if(!noimage)
        ctx.drawImage(scr, middle - iw / 2, middle - ih / 2,  iw, ih);
  }

  stop() {
    const self = this;

    super.stop();

    self.startedAt = false;

    if(self.tictacting) {
      soundManager.stop('tictac');
      self.tictacting = false;
    }

    if(self.isOwner) {
      var xhr = new XMLHttpRequest();
      xhr.open("POST", self.notifyStart, false);
      xhr.send();
    }
  }

  close() {
    const self = this;

    if(self.updateInterval) {
      if(!window.confirm(self.confirmClose))
        return;

      self.stop();
    }
    window.close();
  }

  start(delay_secs) {
    const self = this;

    if(self.updateInterval) {
      if(!window.confirm(self.confirmRestart))
        return;

      self.stop();
      self.draw(true);
    }

    const ctx = self.ctx,
          middle = self.size/2,
          radius = self.radius,
          total_ticks = 1000 * (delay_secs || (60 * self.duration)),
          radiants_per_tick = 2 * Math.PI / total_ticks;
    var pre_alarm_done = false,
        half_game, pre_alarm, last_minute;

    self.tictacting = false;

    function update() {
      const now = Date.now(),
            progress = now - self.startedAt,
            start = 2*Math.PI * progress / 1000 / 60 - Math.PI / 2;

      ctx.beginPath();
      ctx.arc(middle, middle, radius, start-0.2, start + progress * radiants_per_tick);
      ctx.stroke();

      ctx.save();
      ctx.beginPath();
      ctx.lineWidth = self.lineWidth * 0.9;
      if(delay_secs)
        ctx.strokeStyle = 'red';
      else
        ctx.strokeStyle = (pre_alarm && now > pre_alarm
                           ? 'red'
                           : (now > half_game
                              ? 'orange'
                              : 'yellow'));
      ctx.arc(middle, middle, radius, start, start + progress * radiants_per_tick);
      ctx.stroke();
      ctx.restore();

      if(progress < total_ticks) {
        if(!pre_alarm_done && pre_alarm && now > pre_alarm) {
          soundManager.play('prealarm');
          pre_alarm_done = true;
        }
        if(!self.tictacting && now > last_minute) {
          soundManager.play('tictac', { loops: 60 });
          self.tictacting = true;
        }
        self.updateTimeLeft((delay_secs ? delay_secs / 60 : self.duration)
                            - (progress / 1000 / 60));
      } else {
        self.stop();
        if(delay_secs) {
          self.draw(true);
          self.start();
        } else {
          soundManager.play('stop');
          self.terminate();
        }
      }
    }

    if(!self.startedAt) {
      self.startedAt = Date.now();
      if(delay_secs) {
        self.tictacting = true;
        soundManager.play('tictac', { loops: delay_secs });
      } else {
        soundManager.play('start');
        if(self.isOwner) {
          const xhr = new XMLHttpRequest();
          xhr.open("POST", self.notifyStart + '&start', true);
          xhr.send();
        }
      }
    }

    half_game = self.startedAt + 1000 * 30 * self.duration;
    if(self.preAlarm) {
      pre_alarm = self.startedAt + 1000 * 60 * (self.duration - self.preAlarm);
      pre_alarm_done = Date.now() > pre_alarm;
    } else
      pre_alarm = false;
    last_minute = self.startedAt + 1000 * 60 * (self.duration - 1);

    self.drawInterval();
    self.updateInterval = setInterval(update, 1000 / 20);
  }
}
