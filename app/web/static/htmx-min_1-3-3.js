(function(e,t){if(typeof define==="function"&&define.amd){define([],t)}else{e.htmx=t()}})(typeof self!=="undefined"?self:this,function(){return function(){"use strict";var v={onLoad:b,process:rt,on:z,off:V,trigger:lt,ajax:$t,find:S,findAll:E,closest:T,values:function(e,t){var r=Rt(e,t||"post");return r.values},remove:C,addClass:O,removeClass:A,toggleClass:L,takeClass:R,defineExtension:Kt,removeExtension:Qt,logAll:w,logger:null,config:{historyEnabled:true,historyCacheSize:10,refreshOnHistoryMiss:false,defaultSwapStyle:"innerHTML",defaultSwapDelay:0,defaultSettleDelay:100,includeIndicatorStyles:true,indicatorClass:"htmx-indicator",requestClass:"htmx-request",settlingClass:"htmx-settling",swappingClass:"htmx-swapping",allowEval:true,attributesToSettle:["class","style","width","height"],wsReconnectDelay:"full-jitter",disableSelector:"[hx-disable], [data-hx-disable]"},parseInterval:f,_:e,createEventSource:function(e){return new EventSource(e,{withCredentials:true})},createWebSocket:function(e){return new WebSocket(e,[])}};var t=["get","post","put","delete","patch"];var n=t.map(function(e){return"[hx-"+e+"], [data-hx-"+e+"]"}).join(", ");function f(e){if(e==undefined){return undefined}if(e.slice(-2)=="ms"){return parseFloat(e.slice(0,-2))||undefined}if(e.slice(-1)=="s"){return parseFloat(e.slice(0,-1))*1e3||undefined}return parseFloat(e)||undefined}function l(e,t){return e.getAttribute&&e.getAttribute(t)}function a(e,t){return e.hasAttribute&&(e.hasAttribute(t)||e.hasAttribute("data-"+t))}function I(e,t){return l(e,t)||l(e,"data-"+t)}function c(e){return e.parentElement}function M(){return document}function h(e,t){if(t(e)){return e}else if(c(e)){return h(c(e),t)}else{return null}}function k(e,t){var r=null;h(e,function(e){return r=I(e,t)});return r}function d(e,t){var r=e.matches||e.matchesSelector||e.msMatchesSelector||e.mozMatchesSelector||e.webkitMatchesSelector||e.oMatchesSelector;return r&&r.call(e,t)}function r(e){var t=/<([a-z][^\/\0>\x20\t\r\n\f]*)/i;var r=t.exec(e);if(r){return r[1].toLowerCase()}else{return""}}function i(e,t){var r=new DOMParser;var n=r.parseFromString(e,"text/html");var i=n.body;while(t>0){t--;i=i.firstChild}if(i==null){i=M().createDocumentFragment()}return i}function u(e){var t=r(e);switch(t){case"thead":case"tbody":case"tfoot":case"colgroup":case"caption":return i("<table>"+e+"</table>",1);case"col":return i("<table><colgroup>"+e+"</colgroup></table>",2);case"tr":return i("<table><tbody>"+e+"</tbody></table>",2);case"td":case"th":return i("<table><tbody><tr>"+e+"</tr></tbody></table>",3);case"script":return i("<div>"+e+"</div>",1);default:return i(e,0)}}function D(e){if(e){e()}}function o(e,t){return Object.prototype.toString.call(e)==="[object "+t+"]"}function s(e){return o(e,"Function")}function g(e){return o(e,"Object")}function F(e){var t="htmx-internal-data";var r=e[t];if(!r){r=e[t]={}}return r}function p(e){var t=[];if(e){for(var r=0;r<e.length;r++){t.push(e[r])}}return t}function X(e,t){if(e){for(var r=0;r<e.length;r++){t(e[r])}}}function m(e){var t=e.getBoundingClientRect();var r=t.top;var n=t.bottom;return r<window.innerHeight&&n>=0}function P(e){return M().body.contains(e)}function y(e){return e.trim().split(/\s+/)}function U(e,t){for(var r in t){if(t.hasOwnProperty(r)){e[r]=t[r]}}return e}function x(e){try{return JSON.parse(e)}catch(e){ut(e);return null}}function e(e){return Ut(M().body,function(){return eval(e)})}function b(t){var e=v.on("htmx:load",function(e){t(e.detail.elt)});return e}function w(){v.logger=function(e,t,r){if(console){console.log(t,e,r)}}}function S(e,t){if(t){return e.querySelector(t)}else{return S(M(),e)}}function E(e,t){if(t){return e.querySelectorAll(t)}else{return E(M(),e)}}function C(e,t){e=N(e);if(t){setTimeout(function(){C(e)},t)}else{e.parentElement.removeChild(e)}}function O(e,t,r){e=N(e);if(r){setTimeout(function(){O(e,t)},r)}else{e.classList.add(t)}}function A(e,t,r){e=N(e);if(r){setTimeout(function(){A(e,t)},r)}else{e.classList.remove(t)}}function L(e,t){e=N(e);e.classList.toggle(t)}function R(e,t){e=N(e);X(e.parentElement.children,function(e){A(e,t)});O(e,t)}function T(e,t){e=N(e);if(e.closest){return e.closest(t)}else{do{if(e==null||d(e,t)){return e}}while(e=e&&c(e))}}function q(e,t){if(t.indexOf("closest ")===0){return[T(e,t.substr(8))]}else if(t.indexOf("find ")===0){return[S(e,t.substr(5))]}else{return M().querySelectorAll(t)}}function H(e,t){return q(e,t)[0]}function N(e){if(o(e,"String")){return S(e)}else{return e}}function j(e,t,r){if(s(t)){return{target:M().body,event:e,listener:t}}else{return{target:N(e),event:t,listener:r}}}function z(t,r,n){tr(function(){var e=j(t,r,n);e.target.addEventListener(e.event,e.listener)});var e=s(r);return e?r:n}function V(t,r,n){tr(function(){var e=j(t,r,n);e.target.removeEventListener(e.event,e.listener)});return s(r)?r:n}function W(e){var t=h(e,function(e){return I(e,"hx-target")!==null});if(t){var r=I(t,"hx-target");if(r==="this"){return t}else{return H(e,r)}}else{var n=F(e);if(n.boosted){return M().body}else{return e}}}function _(e){var t=v.config.attributesToSettle;for(var r=0;r<t.length;r++){if(e===t[r]){return true}}return false}function B(t,r){X(t.attributes,function(e){if(!r.hasAttribute(e.name)&&_(e.name)){t.removeAttribute(e.name)}});X(r.attributes,function(e){if(_(e.name)){t.setAttribute(e.name,e.value)}})}function $(e,t){var r=er(t);for(var n=0;n<r.length;n++){var i=r[n];try{if(i.isInlineSwap(e)){return true}}catch(e){ut(e)}}return e==="outerHTML"}function J(e,t,r){var n="#"+t.id;var i="outerHTML";if(e==="true"){}else if(e.indexOf(":")>0){i=e.substr(0,e.indexOf(":"));n=e.substr(e.indexOf(":")+1,e.length)}else{i=e}var o=M().querySelector(n);if(o){var a;a=M().createDocumentFragment();a.appendChild(t);if(!$(i,o)){a=t}le(i,o,o,a,r)}else{t.parentNode.removeChild(t);ot(M().body,"htmx:oobErrorNoTarget",{content:t})}return e}function Z(e,r){X(E(e,"[hx-swap-oob], [data-hx-swap-oob]"),function(e){var t=I(e,"hx-swap-oob");if(t!=null){J(t,e,r)}})}function G(e){X(E(e,"[hx-preserve], [data-hx-preserve]"),function(e){var t=I(e,"id");var r=M().getElementById(t);if(r!=null){e.parentNode.replaceChild(r,e)}})}function Y(n,e,i){X(e.querySelectorAll("[id]"),function(e){if(e.id&&e.id.length>0){var t=n.querySelector(e.tagName+"[id='"+e.id+"']");if(t&&t!==n){var r=e.cloneNode();B(e,t);i.tasks.push(function(){B(e,r)})}}})}function K(e){return function(){rt(e);Ke(e);Q(e);lt(e,"htmx:load")}}function Q(e){var t="[autofocus]";var r=d(e,t)?e:e.querySelector(t);if(r!=null){r.focus()}}function ee(e,t,r,n){Y(e,r,n);while(r.childNodes.length>0){var i=r.firstChild;e.insertBefore(i,t);if(i.nodeType!==Node.TEXT_NODE&&i.nodeType!==Node.COMMENT_NODE){n.tasks.push(K(i))}}}function te(t){var e=F(t);if(e.webSocket){e.webSocket.close()}if(e.sseEventSource){e.sseEventSource.close()}if(e.listenerInfos){X(e.listenerInfos,function(e){if(t!==e.on){e.on.removeEventListener(e.trigger,e.listener)}})}if(t.children){X(t.children,function(e){te(e)})}}function re(e,t,r){if(e.tagName==="BODY"){return se(e,t)}else{var n=e.previousSibling;ee(c(e),e,t,r);if(n==null){var i=c(e).firstChild}else{var i=n.nextSibling}F(e).replacedWith=i;r.elts=[];while(i&&i!==e){if(i.nodeType===Node.ELEMENT_NODE){r.elts.push(i)}i=i.nextElementSibling}te(e);c(e).removeChild(e)}}function ne(e,t,r){return ee(e,e.firstChild,t,r)}function ie(e,t,r){return ee(c(e),e,t,r)}function oe(e,t,r){return ee(e,null,t,r)}function ae(e,t,r){return ee(c(e),e.nextSibling,t,r)}function se(e,t,r){var n=e.firstChild;ee(e,n,t,r);if(n){while(n.nextSibling){te(n.nextSibling);e.removeChild(n.nextSibling)}te(n);e.removeChild(n)}}function ue(e,t){var r=k(e,"hx-select");if(r){var n=M().createDocumentFragment();X(t.querySelectorAll(r),function(e){n.appendChild(e)});t=n}return t}function le(e,t,r,n,i){switch(e){case"none":return;case"outerHTML":re(r,n,i);return;case"afterbegin":ne(r,n,i);return;case"beforebegin":ie(r,n,i);return;case"beforeend":oe(r,n,i);return;case"afterend":ae(r,n,i);return;default:var o=er(t);for(var a=0;a<o.length;a++){var s=o[a];try{var u=s.handleSwap(e,r,n,i);if(u){if(typeof u.length!=="undefined"){for(var l=0;l<u.length;l++){var f=u[l];if(f.nodeType!==Node.TEXT_NODE&&f.nodeType!==Node.COMMENT_NODE){i.tasks.push(K(f))}}}return}}catch(e){ut(e)}}se(r,n,i)}}var fe=/<title>([\s\S]+?)<\/title>/im;function ce(e){var t=fe.exec(e);if(t){return t[1]}}function he(e,t,r,n,i){var o=ce(n);if(o){var a=S("title");if(a){a.innerHTML=o}else{window.document.title=o}}var s=u(n);if(s){Z(s,i);s=ue(r,s);G(s);return le(e,r,t,s,i)}}function de(e,t,r){var n=e.getResponseHeader(t);if(n.indexOf("{")===0){var i=x(n);for(var o in i){if(i.hasOwnProperty(o)){var a=i[o];if(!g(a)){a={value:a}}lt(r,o,a)}}}else{lt(r,n,[])}}var ve=/\s/;var ge=/[\s,]/;var pe=/[_$a-zA-Z]/;var me=/[_$a-zA-Z0-9]/;var ye=['"',"'","/"];var xe=/[^\s]/;function be(e){var t=[];var r=0;while(r<e.length){if(pe.exec(e.charAt(r))){var n=r;while(me.exec(e.charAt(r+1))){r++}t.push(e.substr(n,r-n+1))}else if(ye.indexOf(e.charAt(r))!==-1){var i=e.charAt(r);var n=r;r++;while(r<e.length&&e.charAt(r)!==i){if(e.charAt(r)==="\\"){r++}r++}t.push(e.substr(n,r-n+1))}else{var o=e.charAt(r);t.push(o)}r++}return t}function we(e,t,r){return pe.exec(e.charAt(0))&&e!=="true"&&e!=="false"&&e!=="this"&&e!==r&&t!=="."}function Se(e,t,r){if(t[0]==="["){t.shift();var n=1;var i=" return (function("+r+"){ return (";var o=null;while(t.length>0){var a=t[0];if(a==="]"){n--;if(n===0){if(o===null){i=i+"true"}t.shift();i+=")})";try{var s=Ut(e,function(){return Function(i)()},function(){return true});s.source=i;return s}catch(e){ot(M().body,"htmx:syntax:error",{error:e,source:i});return null}}}else if(a==="["){n++}if(we(a,o,r)){i+="(("+r+"."+a+") ? ("+r+"."+a+") : (window."+a+"))"}else{i=i+a}o=t.shift()}}}function Ee(e,t){var r="";while(e.length>0&&!e[0].match(t)){r+=e.shift()}return r}var Ce="input, textarea, select";function Oe(e){var t=I(e,"hx-trigger");var r=[];if(t){var n=be(t);do{Ee(n,xe);var i=n.length;var o=Ee(n,/[,\[\s]/);if(o!==""){if(o==="every"){var a={trigger:"every"};Ee(n,xe);a.pollInterval=f(Ee(n,ve));r.push(a)}else if(o.indexOf("sse:")===0){r.push({trigger:"sse",sseEvent:o.substr(4)})}else{var s={trigger:o};var u=Se(e,n,"event");if(u){s.eventFilter=u}while(n.length>0&&n[0]!==","){Ee(n,xe);var l=n.shift();if(l==="changed"){s.changed=true}else if(l==="once"){s.once=true}else if(l==="consume"){s.consume=true}else if(l==="delay"&&n[0]===":"){n.shift();s.delay=f(Ee(n,ge))}else if(l==="from"&&n[0]===":"){n.shift();s.from=Ee(n,ge)}else if(l==="target"&&n[0]===":"){n.shift();s.target=Ee(n,ge)}else if(l==="throttle"&&n[0]===":"){n.shift();s.throttle=f(Ee(n,ge))}else{ot(e,"htmx:syntax:error",{token:n.shift()})}}r.push(s)}}if(n.length===i){ot(e,"htmx:syntax:error",{token:n.shift()})}Ee(n,xe)}while(n[0]===","&&n.shift())}if(r.length>0){return r}else if(d(e,"form")){return[{trigger:"submit"}]}else if(d(e,Ce)){return[{trigger:"change"}]}else{return[{trigger:"click"}]}}function Ae(e){F(e).cancelled=true}function Le(e,t,r,n){var i=F(e);i.timeout=setTimeout(function(){if(P(e)&&i.cancelled!==true){Jt(t,r,e);Le(e,t,I(e,"hx-"+t),n)}},n)}function Re(e){return location.hostname===e.hostname&&l(e,"href")&&l(e,"href").indexOf("#")!==0}function Te(t,r,e){if(t.tagName==="A"&&Re(t)||t.tagName==="FORM"){r.boosted=true;var n,i;if(t.tagName==="A"){n="get";i=l(t,"href")}else{var o=l(t,"method");n=o?o.toLowerCase():"get";i=l(t,"action")}e.forEach(function(e){Ie(t,n,i,r,e,true)})}}function qe(e){return e.tagName==="FORM"||d(e,'input[type="submit"], button')&&T(e,"form")!==null||e.tagName==="A"&&e.href&&(e.getAttribute("href")==="#"||e.getAttribute("href").indexOf("#")!==0)}function He(e,t){return F(e).boosted&&e.tagName==="A"&&t.type==="click"&&t.ctrlKey}function Ne(e,t){var r=e.eventFilter;if(r){try{return r(t)!==true}catch(e){ot(M().body,"htmx:eventFilter:error",{error:e,source:r.source});return true}}return false}function Ie(n,i,o,e,a,s){var u=n;if(a.from){u=S(a.from)}var l=function(e){if(!P(n)){u.removeEventListener(a.trigger,l);return}if(He(n,e)){return}if(s||qe(n)){e.preventDefault()}if(Ne(a,e)){return}var t=F(e);if(t.handledFor==null){t.handledFor=[]}var r=F(n);if(t.handledFor.indexOf(n)<0){t.handledFor.push(n);if(a.consume){e.stopPropagation()}if(a.target&&e.target){if(!d(e.target,a.target)){return}}if(a.once){if(r.triggeredOnce){return}else{r.triggeredOnce=true}}if(a.changed){if(r.lastValue===n.value){return}else{r.lastValue=n.value}}if(r.delayed){clearTimeout(r.delayed)}if(r.throttle){return}if(a.throttle){r.throttle=setTimeout(function(){Jt(i,o,n,e);r.throttle=null},a.throttle)}else if(a.delay){r.delayed=setTimeout(function(){Jt(i,o,n,e)},a.delay)}else{Jt(i,o,n,e)}}};if(e.listenerInfos==null){e.listenerInfos=[]}e.listenerInfos.push({trigger:a.trigger,listener:l,on:u});u.addEventListener(a.trigger,l)}var Me=false;var ke=null;function De(){if(!ke){ke=function(){Me=true};window.addEventListener("scroll",ke);setInterval(function(){if(Me){Me=false;X(M().querySelectorAll("[hx-trigger='revealed'],[data-hx-trigger='revealed']"),function(e){Fe(e)})}},200)}}function Fe(e){var t=F(e);if(!t.revealed&&m(e)){t.revealed=true;Jt(t.verb,t.path,e)}}function Xe(e,t,r){var n=y(r);for(var i=0;i<n.length;i++){var o=n[i].split(/:(.+)/);if(o[0]==="connect"){Pe(e,o[1],0)}if(o[0]==="send"){je(e)}}}function Pe(s,r,n){if(!P(s)){return}if(r.indexOf("/")==0){var e=location.hostname+(location.port?":"+location.port:"");if(location.protocol=="https:"){r="wss://"+e+r}else if(location.protocol=="http:"){r="ws://"+e+r}}var t=v.createWebSocket(r);t.onerror=function(e){ot(s,"htmx:wsError",{error:e,socket:t});Ue(s)};t.onclose=function(e){if([1006,1012,1013].includes(e.code)){var t=ze(n);setTimeout(function(){Pe(s,r,n+1)},t)}};t.onopen=function(e){n=0};F(s).webSocket=t;t.addEventListener("message",function(e){if(Ue(s)){return}var t=e.data;st(s,function(e){t=e.transformResponse(t,null,s)});var r=Ft(s);var n=u(t);var i=p(n.children);for(var o=0;o<i.length;o++){var a=i[o];J(I(a,"hx-swap-oob")||"true",a,r)}mt(r.tasks)})}function Ue(e){if(!P(e)){F(e).webSocket.close();return true}}function je(l){var f=h(l,function(e){return F(e).webSocket!=null});if(f){l.addEventListener(Oe(l)[0].trigger,function(e){var t=F(f).webSocket;var r=Nt(l,f);var n=Rt(l,"post");var i=n.errors;var o=n.values;var a=Vt(l);var s=U(o,a);var u=It(s,l);u["HEADERS"]=r;if(i&&i.length>0){lt(l,"htmx:validation:halted",i);return}t.send(JSON.stringify(u));if(qe(l)){e.preventDefault()}})}else{ot(l,"htmx:noWebSocketSourceError")}}function ze(e){var t=v.config.wsReconnectDelay;if(typeof t==="function"){return t(e)}if(t==="full-jitter"){var r=Math.min(e,6);var n=1e3*Math.pow(2,r);return n*Math.random()}ut('htmx.config.wsReconnectDelay must either be a function or the string "full-jitter"')}function Ve(e,t,r){var n=y(r);for(var i=0;i<n.length;i++){var o=n[i].split(/:(.+)/);if(o[0]==="connect"){We(e,o[1])}if(o[0]==="swap"){_e(e,o[1])}}}function We(t,e){var r=v.createEventSource(e);r.onerror=function(e){ot(t,"htmx:sseError",{error:e,source:r});$e(t)};F(t).sseEventSource=r}function _e(o,a){var s=h(o,Je);if(s){var u=F(s).sseEventSource;var l=function(e){if($e(s)){u.removeEventListener(a,l);return}var t=e.data;st(o,function(e){t=e.transformResponse(t,null,o)});var r=kt(o);var n=W(o);var i=Ft(o);he(r.swapStyle,o,n,t,i);mt(i.tasks);lt(o,"htmx:sseMessage",e)};F(o).sseListener=l;u.addEventListener(a,l)}else{ot(o,"htmx:noSSESourceError")}}function Be(e,t,r,n){var i=h(e,Je);if(i){var o=F(i).sseEventSource;var a=function(){if(!$e(i)){if(P(e)){Jt(t,r,e)}else{o.removeEventListener(n,a)}}};F(e).sseListener=a;o.addEventListener(n,a)}else{ot(e,"htmx:noSSESourceError")}}function $e(e){if(!P(e)){F(e).sseEventSource.close();return true}}function Je(e){return F(e).sseEventSource!=null}function Ze(e,t,r,n,i){var o=function(){if(!n.loaded){n.loaded=true;Jt(t,r,e)}};if(i){setTimeout(o,i)}else{o()}}function Ge(n,i,e){var o=false;X(t,function(t){if(a(n,"hx-"+t)){var r=I(n,"hx-"+t);o=true;i.path=r;i.verb=t;e.forEach(function(e){if(e.sseEvent){Be(n,t,r,e.sseEvent)}else if(e.trigger==="revealed"){De();Fe(n)}else if(e.trigger==="load"){Ze(n,t,r,i,e.delay)}else if(e.pollInterval){i.polling=true;Le(n,t,r,e.pollInterval)}else{Ie(n,t,r,i,e)}})}});return o}function Ye(e){if(e.type==="text/javascript"||e.type===""){try{Ut(e,function(){Function(e.innerText)()})}catch(e){ut(e)}}}function Ke(e){if(d(e,"script")){Ye(e)}X(E(e,"script"),function(e){Ye(e)})}function Qe(){return document.querySelector("[hx-boost], [data-hx-boost]")}function et(e){if(e.querySelectorAll){var t=Qe()?", a, form":"";var r=e.querySelectorAll(n+t+", [hx-sse], [data-hx-sse], [hx-ws],"+" [data-hx-ws]");return r}else{return[]}}function tt(e){if(e.closest&&e.closest(v.config.disableSelector)){return}var t=F(e);if(!t.initialized){t.initialized=true;lt(e,"htmx:beforeProcessNode");if(e.value){t.lastValue=e.value}var r=Oe(e);var n=Ge(e,t,r);if(!n&&k(e,"hx-boost")==="true"){Te(e,t,r)}var i=I(e,"hx-sse");if(i){Ve(e,t,i)}var o=I(e,"hx-ws");if(o){Xe(e,t,o)}lt(e,"htmx:afterProcessNode")}}function rt(e){e=N(e);tt(e);X(et(e),function(e){tt(e)})}function nt(e){return e.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase()}function it(e,t){var r;if(window.CustomEvent&&typeof window.CustomEvent==="function"){r=new CustomEvent(e,{bubbles:true,cancelable:true,detail:t})}else{r=M().createEvent("CustomEvent");r.initCustomEvent(e,true,true,t)}return r}function ot(e,t,r){lt(e,t,U({error:t},r))}function at(e){return e==="htmx:afterProcessNode"}function st(e,t){X(er(e),function(e){try{t(e)}catch(e){ut(e)}})}function ut(e){if(console.error){console.error(e)}else if(console.log){console.log("ERROR: ",e)}}function lt(e,t,r){e=N(e);if(r==null){r={}}r["elt"]=e;var n=it(t,r);if(v.logger&&!at(t)){v.logger(e,t,r)}if(r.error){ut(r.error);lt(e,"htmx:error",{errorInfo:r})}var i=e.dispatchEvent(n);var o=nt(t);if(i&&o!==t){var a=it(o,n.detail);i=i&&e.dispatchEvent(a)}st(e,function(e){i=i&&e.onEvent(t,n)!==false});return i}var ft=null;function ct(){var e=M().querySelector("[hx-history-elt],[data-hx-history-elt]");return e||M().body}function ht(e,t,r,n){var i=x(localStorage.getItem("htmx-history-cache"))||[];for(var o=0;o<i.length;o++){if(i[o].url===e){i.splice(o,1);break}}i.push({url:e,content:t,title:r,scroll:n});while(i.length>v.config.historyCacheSize){i.shift()}while(i.length>0){try{localStorage.setItem("htmx-history-cache",JSON.stringify(i));break}catch(e){ot(M().body,"htmx:historyCacheError",{cause:e,cache:i});i.shift()}}}function dt(e){var t=x(localStorage.getItem("htmx-history-cache"))||[];for(var r=0;r<t.length;r++){if(t[r].url===e){return t[r]}}return null}function vt(e){var t=v.config.requestClass;var r=e.cloneNode(true);X(E(r,"."+t),function(e){A(e,t)});return r.innerHTML}function gt(){var e=ct();var t=ft||location.pathname+location.search;lt(M().body,"htmx:beforeHistorySave",{path:t,historyElt:e});if(v.config.historyEnabled)history.replaceState({htmx:true},M().title,window.location.href);ht(t,vt(e),M().title,window.scrollY)}function pt(e){if(v.config.historyEnabled)history.pushState({htmx:true},"",e);ft=e}function mt(e){X(e,function(e){e.call()})}function yt(n){var e=new XMLHttpRequest;var i={path:n,xhr:e};lt(M().body,"htmx:historyCacheMiss",i);e.open("GET",n,true);e.setRequestHeader("HX-History-Restore-Request","true");e.onload=function(){if(this.status>=200&&this.status<400){lt(M().body,"htmx:historyCacheMissLoad",i);var e=u(this.response);e=e.querySelector("[hx-history-elt],[data-hx-history-elt]")||e;var t=ct();var r=Ft(t);se(t,e,r);mt(r.tasks);ft=n;lt(M().body,"htmx:historyRestore",{path:n})}else{ot(M().body,"htmx:historyCacheMissLoadError",i)}};e.send()}function xt(e){gt();e=e||location.pathname+location.search;var t=dt(e);if(t){var r=u(t.content);var n=ct();var i=Ft(n);se(n,r,i);mt(i.tasks);document.title=t.title;window.scrollTo(0,t.scroll);ft=e;lt(M().body,"htmx:historyRestore",{path:e})}else{if(v.config.refreshOnHistoryMiss){window.location.reload(true)}else{yt(e)}}}function bt(e){var t=k(e,"hx-push-url");return t&&t!=="false"||e.tagName==="A"&&F(e).boosted}function wt(e){var t=k(e,"hx-push-url");return t==="true"||t==="false"?null:t}function St(e){var t=k(e,"hx-indicator");if(t){var r=q(e,t)}else{r=[e]}X(r,function(e){e.classList["add"].call(e.classList,v.config.requestClass)});return r}function Et(e){X(e,function(e){e.classList["remove"].call(e.classList,v.config.requestClass)})}function Ct(e,t){for(var r=0;r<e.length;r++){var n=e[r];if(n.isSameNode(t)){return true}}return false}function Ot(e){if(e.name===""||e.name==null||e.disabled){return false}if(e.type==="button"||e.type==="submit"||e.tagName==="image"||e.tagName==="reset"||e.tagName==="file"){return false}if(e.type==="checkbox"||e.type==="radio"){return e.checked}return true}function At(t,r,n,e,i){if(e==null||Ct(t,e)){return}else{t.push(e)}if(Ot(e)){var o=l(e,"name");var a=e.value;if(e.multiple){a=p(e.querySelectorAll("option:checked")).map(function(e){return e.value})}if(e.files){a=p(e.files)}if(o!=null&&a!=null){var s=r[o];if(s){if(Array.isArray(s)){if(Array.isArray(a)){r[o]=s.concat(a)}else{s.push(a)}}else{if(Array.isArray(a)){r[o]=[s].concat(a)}else{r[o]=[s,a]}}}else{r[o]=a}}if(i){Lt(e,n)}}if(d(e,"form")){var u=e.elements;X(u,function(e){At(t,r,n,e,i)})}}function Lt(e,t){if(e.willValidate){lt(e,"htmx:validation:validate");if(!e.checkValidity()){t.push({elt:e,message:e.validationMessage,validity:e.validity});lt(e,"htmx:validation:failed",{message:e.validationMessage,validity:e.validity})}}}function Rt(e,t){var r=[];var n={};var i={};var o=[];var a=d(e,"form")&&e.noValidate!==true;if(t!=="get"){At(r,i,o,T(e,"form"),a)}At(r,n,o,e,a);var s=k(e,"hx-include");if(s){var u=q(e,s);X(u,function(e){At(r,n,o,e,a);if(!d(e,"form")){X(e.querySelectorAll(Ce),function(e){At(r,n,o,e,a)})}})}n=U(n,i);return{errors:o,values:n}}function Tt(e,t,r){if(e!==""){e+="&"}e+=encodeURIComponent(t)+"="+encodeURIComponent(r);return e}function qt(e){var t="";for(var r in e){if(e.hasOwnProperty(r)){var n=e[r];if(Array.isArray(n)){X(n,function(e){t=Tt(t,r,e)})}else{t=Tt(t,r,n)}}}return t}function Ht(e){var t=new FormData;for(var r in e){if(e.hasOwnProperty(r)){var n=e[r];if(Array.isArray(n)){X(n,function(e){t.append(r,e)})}else{t.append(r,n)}}}return t}function Nt(e,t,r){var n={"HX-Request":"true","HX-Trigger":l(e,"id"),"HX-Trigger-Name":l(e,"name"),"HX-Target":I(t,"id"),"HX-Current-URL":M().location.href};Pt(e,"hx-headers",false,n);if(r!==undefined){n["HX-Prompt"]=r}return n}function It(t,e){var r=k(e,"hx-params");if(r){if(r==="none"){return{}}else if(r==="*"){return t}else if(r.indexOf("not ")===0){X(r.substr(4).split(","),function(e){e=e.trim();delete t[e]});return t}else{var n={};X(r.split(","),function(e){e=e.trim();n[e]=t[e]});return n}}else{return t}}function Mt(e){return l(e,"href")&&l(e,"href").indexOf("#")>=0}function kt(e){var t=k(e,"hx-swap");var r={swapStyle:F(e).boosted?"innerHTML":v.config.defaultSwapStyle,swapDelay:v.config.defaultSwapDelay,settleDelay:v.config.defaultSettleDelay};if(F(e).boosted&&!Mt(e)){r["show"]="top"}if(t){var n=y(t);if(n.length>0){r["swapStyle"]=n[0];for(var i=1;i<n.length;i++){var o=n[i];if(o.indexOf("swap:")===0){r["swapDelay"]=f(o.substr(5))}if(o.indexOf("settle:")===0){r["settleDelay"]=f(o.substr(7))}if(o.indexOf("scroll:")===0){r["scroll"]=o.substr(7)}if(o.indexOf("show:")===0){r["show"]=o.substr(5)}}}}return r}function Dt(t,r,n){var i=null;st(r,function(e){if(i==null){i=e.encodeParameters(t,n,r)}});if(i!=null){return i}else{if(k(r,"hx-encoding")==="multipart/form-data"){return Ht(n)}else{return qt(n)}}}function Ft(e){return{tasks:[],elts:[e]}}function Xt(e,t){var r=e[0];var n=e[e.length-1];if(t.scroll){if(t.scroll==="top"&&r){r.scrollTop=0}if(t.scroll==="bottom"&&n){n.scrollTop=n.scrollHeight}}if(t.show){if(t.show==="top"&&r){r.scrollIntoView(true)}if(t.show==="bottom"&&n){n.scrollIntoView(false)}}}function Pt(e,t,r,n){if(n==null){n={}}if(e==null){return n}var i=I(e,t);if(i){var o=i.trim();var a=r;if(o.indexOf("javascript:")===0){o=o.substr(11);a=true}if(o.indexOf("{")!==0){o="{"+o+"}"}var s;if(a){s=Ut(e,function(){return Function("return ("+o+")")()},{})}else{s=x(o)}for(var u in s){if(s.hasOwnProperty(u)){if(n[u]==null){n[u]=s[u]}}}}return Pt(c(e),t,r,n)}function Ut(e,t,r){if(v.config.allowEval){return t()}else{ot(e,"htmx:evalDisallowedError");return r}}function jt(e,t){return Pt(e,"hx-vars",true,t)}function zt(e,t){return Pt(e,"hx-vals",false,t)}function Vt(e){return U(jt(e),zt(e))}function Wt(t,r,n){if(n!==null){try{t.setRequestHeader(r,n)}catch(e){t.setRequestHeader(r,encodeURIComponent(n));t.setRequestHeader(r+"-URI-AutoEncoded","true")}}}function _t(t){if(t.responseURL&&typeof URL!=="undefined"){try{var e=new URL(t.responseURL);return e.pathname+e.search}catch(e){ot(M().body,"htmx:badResponseUrl",{url:t.responseURL})}}}function Bt(e,t){return e.getAllResponseHeaders().match(t)}function $t(e,t,r){if(r){if(r instanceof Element||o(r,"String")){return Jt(e,t,null,null,{targetOverride:N(r)})}else{return Jt(e,t,N(r.source),r.event,{handler:r.handler,headers:r.headers,values:r.values,targetOverride:N(r.target)})}}else{return Jt(e,t)}}function Jt(e,t,r,n,i){var o=null;var a=null;i=i!=null?i:{};if(typeof Promise!=="undefined"){var s=new Promise(function(e,t){o=e;a=t})}if(r==null){r=M().body}var u=i.handler||Zt;if(!P(r)){return}var l=i.targetOverride||W(r);if(l==null){ot(r,"htmx:targetError",{target:I(r,"hx-target")});return}var f=F(r);if(f.requestInFlight){f.queuedRequest=function(){Jt(e,t,r,n)};return}else{f.requestInFlight=true}var c=function(){f.requestInFlight=false;var e=f.queuedRequest;f.queuedRequest=null;if(e){e()}};var h=k(r,"hx-prompt");if(h){var d=prompt(h);if(d===null||!lt(r,"htmx:prompt",{prompt:d,target:l}))D(o);c();return s}var v=k(r,"hx-confirm");if(v){if(!confirm(v)){D(o);c();return s}}var g=new XMLHttpRequest;var p=Nt(r,l,d);if(i.headers){p=U(p,i.values)}var m=Rt(r,e);var y=m.errors;var x=m.values;if(i.values){x=U(x,i.values)}var b=Vt(r);var w=U(x,b);var S=It(w,r);if(e!=="get"&&k(r,"hx-encoding")==null){p["Content-Type"]="application/x-www-form-urlencoded; charset=UTF-8"}if(t==null||t===""){t=M().location.href}var E={parameters:S,unfilteredParameters:w,headers:p,target:l,verb:e,errors:y,path:t,triggeringEvent:n};if(!lt(r,"htmx:configRequest",E))return c();t=E.path;e=E.verb;p=E.headers;S=E.parameters;y=E.errors;if(y&&y.length>0){lt(r,"htmx:validation:halted",E);D(o);c();return s}var C=t.split("#");var O=C[0];var A=C[1];if(e==="get"){var L=O;var R=Object.keys(S).length!==0;if(R){if(L.indexOf("?")<0){L+="?"}else{L+="&"}L+=qt(S);if(A){L+="#"+A}}g.open("GET",L,true)}else{g.open(e.toUpperCase(),t,true)}g.overrideMimeType("text/html");for(var T in p){if(p.hasOwnProperty(T)){var q=p[T];Wt(g,T,q)}}var H={xhr:g,target:l,requestConfig:E,pathInfo:{path:t,finalPath:L,anchor:A}};g.onload=function(){try{u(r,H)}catch(e){ot(r,"htmx:onLoadError",U({error:e},H));throw e}finally{Et(N);var e=r;if(!P(r)){e=F(l).replacedWith||l}lt(e,"htmx:afterRequest",H);lt(e,"htmx:afterOnLoad",H);D(o);c()}};g.onerror=function(){Et(N);var e=r;if(!P(r)){e=F(l).replacedWith||l}ot(e,"htmx:afterRequest",H);ot(e,"htmx:sendError",H);D(a);c()};g.onabort=function(){Et(N);var e=r;if(!P(r)){e=F(l).replacedWith||l}ot(e,"htmx:afterRequest",H);ot(e,"htmx:sendAbort",H);D(a);c()};if(!lt(r,"htmx:beforeRequest",H)){D(o);c();return s}var N=St(r);X(["loadstart","loadend","progress","abort"],function(t){X([g,g.upload],function(e){e.addEventListener(t,function(e){lt(r,"htmx:xhr:"+t,{lengthComputable:e.lengthComputable,loaded:e.loaded,total:e.total})})})});lt(r,"htmx:beforeSend",H);g.send(e==="get"?null:Dt(g,r,S));return s}function Zt(a,s){var u=s.xhr;var l=s.target;if(!lt(a,"htmx:beforeOnLoad",s))return;if(Bt(u,/HX-Trigger:/i)){de(u,"HX-Trigger",a)}if(Bt(u,/HX-Push:/i)){var f=u.getResponseHeader("HX-Push")}if(Bt(u,/HX-Redirect:/i)){window.location.href=u.getResponseHeader("HX-Redirect");return}if(Bt(u,/HX-Refresh:/i)){if("true"===u.getResponseHeader("HX-Refresh")){location.reload();return}}var c=bt(a)||f;if(u.status>=200&&u.status<400){if(u.status===286){Ae(a)}if(u.status!==204){if(!lt(l,"htmx:beforeSwap",s))return;var h=u.response;st(a,function(e){h=e.transformResponse(h,u,a)});if(c){gt()}var d=kt(a);l.classList.add(v.config.swappingClass);var e=function(){try{var e=document.activeElement;var t={elt:e,start:e?e.selectionStart:null,end:e?e.selectionEnd:null};var r=Ft(l);he(d.swapStyle,l,a,h,r);if(t.elt&&!P(t.elt)&&t.elt.id){var n=document.getElementById(t.elt.id);if(n){if(t.start&&n.setSelectionRange){n.setSelectionRange(t.start,t.end)}n.focus()}}l.classList.remove(v.config.swappingClass);X(r.elts,function(e){if(e.classList){e.classList.add(v.config.settlingClass)}lt(e,"htmx:afterSwap",s)});if(s.pathInfo.anchor){location.hash=s.pathInfo.anchor}if(Bt(u,/HX-Trigger-After-Swap:/i)){var i=a;if(!P(a)){i=M().body}de(u,"HX-Trigger-After-Swap",i)}var o=function(){X(r.tasks,function(e){e.call()});X(r.elts,function(e){if(e.classList){e.classList.remove(v.config.settlingClass)}lt(e,"htmx:afterSettle",s)});if(c){var e=f||wt(a)||_t(u)||s.pathInfo.finalPath||s.pathInfo.path;pt(e);lt(M().body,"htmx:pushedIntoHistory",{path:e})}Xt(r.elts,d);if(Bt(u,/HX-Trigger-After-Settle:/i)){var t=a;if(!P(a)){t=M().body}de(u,"HX-Trigger-After-Settle",t)}};if(d.settleDelay>0){setTimeout(o,d.settleDelay)}else{o()}}catch(e){ot(a,"htmx:swapError",s);throw e}};if(d.swapDelay>0){setTimeout(e,d.swapDelay)}else{e()}}}else{ot(a,"htmx:responseError",U({error:"Response Status Error Code "+u.status+" from "+s.pathInfo.path},s))}}var Gt={};function Yt(){return{onEvent:function(e,t){return true},transformResponse:function(e,t,r){return e},isInlineSwap:function(e){return false},handleSwap:function(e,t,r,n){return false},encodeParameters:function(e,t,r){return null}}}function Kt(e,t){Gt[e]=U(Yt(),t)}function Qt(e){delete Gt[e]}function er(e,r,n){if(e==undefined){return r}if(r==undefined){r=[]}if(n==undefined){n=[]}var t=I(e,"hx-ext");if(t){X(t.split(","),function(e){e=e.replace(/ /g,"");if(e.slice(0,7)=="ignore:"){n.push(e.slice(7));return}if(n.indexOf(e)<0){var t=Gt[e];if(t&&r.indexOf(t)<0){r.push(t)}}})}return er(c(e),r,n)}function tr(e){if(M().readyState!=="loading"){e()}else{M().addEventListener("DOMContentLoaded",e)}}function rr(){if(v.config.includeIndicatorStyles!==false){M().head.insertAdjacentHTML("beforeend","<style>                      ."+v.config.indicatorClass+"{opacity:0;transition: opacity 200ms ease-in;}                      ."+v.config.requestClass+" ."+v.config.indicatorClass+"{opacity:1}                      ."+v.config.requestClass+"."+v.config.indicatorClass+"{opacity:1}                    </style>")}}function nr(){var e=M().querySelector('meta[name="htmx-config"]');if(e){return x(e.content)}else{return null}}function ir(){var e=nr();if(e){v.config=U(v.config,e)}}tr(function(){ir();rr();var e=M().body;rt(e);window.onpopstate=function(e){if(e.state&&e.state.htmx){xt()}};setTimeout(function(){lt(e,"htmx:load",{})},0)});return v}()});