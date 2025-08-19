"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[4313],{6694:(e,t,a)=>{a.d(t,{Ay:()=>n.A});var n=a(66492);a(61972)},13817:(e,t,a)=>{a.d(t,{A:()=>d,v:()=>r});var n=a(2445),l=a(96540),i=a(23576);const r=()=>{var e;return null==(e=document.getElementById("controlSections"))?void 0:e.lastElementChild},o=e=>{var t,a;const n=null==(t=window)?void 0:t.innerHeight,l=null==(a=window)?void 0:a.innerWidth,i=null==e?void 0:e.getBoundingClientRect();return n&&l&&null!=i&&i.top?{yRatio:i.top/n,xRatio:i.left/l}:{yRatio:0,xRatio:0}},d=({getPopupContainer:e,getVisibilityRatio:t=o,open:a,destroyTooltipOnHide:d=!1,placement:c="right",...s})=>{const u=(0,l.useRef)(),[h,p]=(0,l.useState)(void 0===a?s.defaultOpen:a),[m,v]=l.useState(c),g=(0,l.useCallback)((()=>{if(!u.current)return;const{yRatio:e,xRatio:a}=t(u.current),n=a<.35?"right":a>.65?"left":"",l=e<.35?n?"top":"bottom":e>.65?n?"bottom":"top":"",i=(n?n+l.charAt(0).toUpperCase()+l.slice(1):l)||"left";i!==m&&v(i)}),[t]),f=(0,l.useCallback)((e=>{const t=r();t&&t.style.setProperty("overflow-y",e?"hidden":"auto","important")}),[g]),C=(0,l.useCallback)((t=>(u.current=t,(null==e?void 0:e(t))||document.body)),[g,e]),b=(0,l.useCallback)((e=>{void 0===e&&f(e),p(!!e),null==s.onOpenChange||s.onOpenChange(!!e)}),[s,f]),Y=(0,l.useCallback)((e=>{"Escape"===e.key&&(p(!1),null==s.onOpenChange||s.onOpenChange(!1))}),[s]);return(0,l.useEffect)((()=>{void 0!==a&&p(!!a)}),[a]),(0,l.useEffect)((()=>{void 0!==h&&f(h)}),[h,f]),(0,l.useEffect)((()=>(h&&document.addEventListener("keydown",Y),()=>{document.removeEventListener("keydown",Y)})),[Y,h]),(0,l.useEffect)((()=>{h&&g()}),[h,g]),(0,n.Y)(i.A,{...s,open:h,arrow:{pointAtCenter:!0},placement:m,onOpenChange:b,getPopupContainer:C,destroyTooltipOnHide:d})}},36188:(e,t,a)=>{a.d(t,{c:()=>r});var n=a(2445),l=a(17437),i=a(36552);function r(e){return(0,n.Y)(i.A,{css:e=>l.AH`
        margin: ${e.margin}px 0;
      `,...e})}},49231:(e,t,a)=>{a.d(t,{RV:()=>s,be:()=>r,cJ:()=>c,ke:()=>d,kw:()=>u,o6:()=>i,oF:()=>l,sw:()=>n,u_:()=>o});const n="previous calendar week",l="previous calendar month",i="previous calendar quarter",r="previous calendar year",o="Current day",d="Current week",c="Current month",s="Current year",u="Current quarter"},61972:(e,t,a)=>{a.d(t,{cn:()=>c,oo:()=>b,nS:()=>s,z6:()=>o,Be:()=>C,OL:()=>d,yI:()=>Y,ZC:()=>u,Ex:()=>h,c1:()=>y,BJ:()=>r,bd:()=>w,IZ:()=>m,Wm:()=>g,s6:()=>v,OP:()=>f,IS:()=>E,Ab:()=>S,J5:()=>O,IM:()=>I});var n=a(59674),l=a(74098),i=a(49231);const r=[{value:"Common",label:(0,l.t)("Last")},{value:"Calendar",label:(0,l.t)("Previous")},{value:"Current",label:(0,l.t)("Current")},{value:"Custom",label:(0,l.t)("Custom")},{value:"Advanced",label:(0,l.t)("Advanced")},{value:"No filter",label:(0,l.t)("No filter")}],o=[{value:"Last day",label:(0,l.t)("Last day")},{value:"Last week",label:(0,l.t)("Last week")},{value:"Last month",label:(0,l.t)("Last month")},{value:"Last quarter",label:(0,l.t)("Last quarter")},{value:"Last year",label:(0,l.t)("Last year")}],d=new Set(o.map((e=>e.value))),c=[{value:i.sw,label:(0,l.t)("previous calendar week")},{value:i.oF,label:(0,l.t)("previous calendar month")},{value:i.o6,label:(0,l.t)("previous calendar quarter")},{value:i.be,label:(0,l.t)("previous calendar year")}],s=new Set(c.map((e=>e.value))),u=[{value:i.u_,label:(0,l.t)("Current day")},{value:i.ke,label:(0,l.t)("Current week")},{value:i.cJ,label:(0,l.t)("Current month")},{value:i.kw,label:(0,l.t)("Current quarter")},{value:i.RV,label:(0,l.t)("Current year")}],h=new Set(u.map((e=>e.value))),p=[{value:"second",label:e=>(0,l.t)("Seconds %s",e)},{value:"minute",label:e=>(0,l.t)("Minutes %s",e)},{value:"hour",label:e=>(0,l.t)("Hours %s",e)},{value:"day",label:e=>(0,l.t)("Days %s",e)},{value:"week",label:e=>(0,l.t)("Weeks %s",e)},{value:"month",label:e=>(0,l.t)("Months %s",e)},{value:"quarter",label:e=>(0,l.t)("Quarters %s",e)},{value:"year",label:e=>(0,l.t)("Years %s",e)}],m=p.map((e=>({value:e.value,label:e.label((0,l.t)("Before"))}))),v=p.map((e=>({value:e.value,label:e.label((0,l.t)("After"))}))),g=[{value:"specific",label:(0,l.t)("Specific Date/Time")},{value:"relative",label:(0,l.t)("Relative Date/Time")},{value:"now",label:(0,l.t)("Now")},{value:"today",label:(0,l.t)("Midnight")}],f=g.slice(),C=new Set(["Last day","Last week","Last month","Last quarter","Last year"]),b=new Set([i.sw,i.oF,i.o6,i.be]),Y=new Set([i.u_,i.ke,i.cJ,i.kw,i.RV]),y="YYYY-MM-DD[T]HH:mm:ss",w=((0,n.XV)().utc().startOf("day").subtract(7,"days").format(y),(0,n.XV)().utc().startOf("day").format(y));var A;!function(e){e.CommonFrame="common-frame",e.ModalOverlay="modal-overlay",e.PopoverOverlay="time-range-trigger",e.NoFilter="no-filter",e.CancelButton="cancel-button",e.ApplyButton="date-filter-control__apply-button"}(A||(A={}));const x=String.raw`\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:(?:[+-]\d\d:\d\d)|Z)?`,D=String.raw`(?:TODAY|NOW)`,F=(RegExp(String.raw`^${x}$|^${D}$`,"i"),["specific","today","now"]),S=e=>"now"===e?(0,n.XV)().utc().startOf("second"):"today"===e?(0,n.XV)().utc().startOf("day"):(0,n.XV)(e),$=e=>S(e).format(y),E=e=>{const{sinceDatetime:t,sinceMode:a,sinceGrain:n,sinceGrainValue:l,untilDatetime:i,untilMode:r,untilGrain:o,untilGrainValue:d,anchorValue:c}={...e};if(F.includes(a)&&F.includes(r))return`${"specific"===a?$(t):a} : ${"specific"===r?$(i):r}`;if(F.includes(a)&&"relative"===r){const e="specific"===a?$(t):a;return`${e} : DATEADD(DATETIME("${e}"), ${d}, ${o})`}if("relative"===a&&F.includes(r)){const e="specific"===r?$(i):r;return`DATEADD(DATETIME("${e}"), ${-Math.abs(l)}, ${n}) : ${e}`}return`DATEADD(DATETIME("${c}"), ${-Math.abs(l)}, ${n}) : DATEADD(DATETIME("${c}"), ${d}, ${o})`};var T=a(31463),N=a(39242),k=a(61225);const O=e=>d.has(e)?"Common":s.has(e)?"Calendar":h.has(e)?"Current":e===T.WC?"No filter":(0,N.t)(e).matchedFlag?"Custom":"Advanced";function I(){var e;return null!=(e=(0,k.d4)((e=>{var t;return null==e||null==(t=e.common)||null==(t=t.conf)?void 0:t.DEFAULT_TIME_FILTER})))?e:T.WC}},66492:(e,t,a)=>{a.d(t,{A:()=>X});var n=a(2445),l=a(96540),i=a(50290),r=a(17437),o=a(39591),d=a(31463),c=a(20033),s=a(74098),u=a(2801),h=a(23575),p=a(36188),m=a(88217),v=a(95018),g=a(97163),f=a(18865),C=a(8558),b=a(28674),Y=a(93590),y=a(51692),w=a(13817),A=a(61972),x=a(22750);function D(e){let t="Last week";return A.Be.has(e.value)?t=e.value:e.onChange(t),(0,n.FD)(n.FK,{children:[(0,n.Y)("div",{className:"section-title",children:(0,s.t)("Configure Time Range: Last...")}),(0,n.Y)(x.s.GroupWrapper,{spaceConfig:{direction:"vertical",size:15,align:"start",wrap:!1},size:"large",value:t,onChange:t=>e.onChange(t.target.value),options:A.z6})]})}var F=a(49231);function S({onChange:e,value:t}){return(0,l.useEffect)((()=>{A.oo.has(t)||e(F.sw)}),[e,t]),A.oo.has(t)?(0,n.FD)(n.FK,{children:[(0,n.Y)("div",{className:"section-title",children:(0,s.t)("Configure Time Range: Previous...")}),(0,n.Y)(x.s.GroupWrapper,{spaceConfig:{direction:"vertical",size:15,align:"start",wrap:!1},size:"large",value:t,onChange:t=>e(t.target.value),options:A.cn})]}):null}function $({onChange:e,value:t}){return(0,l.useEffect)((()=>{A.yI.has(t)||e(F.ke)}),[t]),A.yI.has(t)?(0,n.FD)(n.FK,{children:[(0,n.Y)("div",{className:"section-title",children:(0,s.t)("Configure Time Range: Current...")}),(0,n.Y)(x.s.GroupWrapper,{spaceConfig:{direction:"vertical",size:15,align:"start",wrap:!0},size:"large",onChange:t=>{let a=t.target.value;a=a.trim(),""!==a&&e(a)},options:A.ZC})]}):null}var E=a(39242),T=a(92998),N=a(20668),k=a(47152),O=a(16370),I=a(5250),L=a(64535),M=a(7142),R=a(89064);function z(e){const{customRange:t,matchedFlag:a}=(0,E.t)(e.value),l=(0,R.Y)();a||e.onChange((0,A.IS)(t));const{sinceDatetime:i,sinceMode:r,sinceGrain:o,sinceGrainValue:d,untilDatetime:c,untilMode:h,untilGrain:p,untilGrainValue:m,anchorValue:v,anchorMode:g}={...t};function f(a,n){e.onChange((0,A.IS)({...t,[a]:n}))}function C(a,n){"number"==typeof n&&Number.isInteger(n)&&n>0&&e.onChange((0,A.IS)({...t,[a]:n}))}return null===l?(0,n.Y)(T.R,{position:"inline-centered"}):(0,n.Y)(N.Q,{locale:l,children:(0,n.FD)("div",{children:[(0,n.Y)("div",{className:"section-title",children:(0,s.t)("Configure custom time range")}),(0,n.FD)(k.A,{gutter:24,children:[(0,n.FD)(O.A,{span:12,children:[(0,n.FD)("div",{className:"control-label",children:[(0,s.t)("Start (inclusive)")," ",(0,n.Y)(I.I,{tooltip:(0,s.t)("Start date included in time range"),placement:"right"})]}),(0,n.Y)(u.A,{ariaLabel:(0,s.t)("Start (inclusive)"),options:A.Wm,value:r,onChange:e=>f("sinceMode",e)}),"specific"===r&&(0,n.Y)(k.A,{children:(0,n.Y)(L.l,{showTime:!0,defaultValue:(0,A.Ab)(i),onChange:e=>f("sinceDatetime",e.format(A.c1)),allowClear:!1,getPopupContainer:t=>e.isOverflowingFilterBar?t.parentNode:document.body})}),"relative"===r&&(0,n.FD)(k.A,{gutter:8,children:[(0,n.Y)(O.A,{span:11,children:(0,n.Y)(M.A,{placeholder:(0,s.t)("Relative quantity"),value:Math.abs(d),min:1,defaultValue:1,onChange:e=>C("sinceGrainValue",e||1),onStep:e=>C("sinceGrainValue",e||1)})}),(0,n.Y)(O.A,{span:13,children:(0,n.Y)(u.A,{ariaLabel:(0,s.t)("Relative period"),options:A.IZ,value:o,onChange:e=>f("sinceGrain",e)})})]})]}),(0,n.FD)(O.A,{span:12,children:[(0,n.FD)("div",{className:"control-label",children:[(0,s.t)("End (exclusive)")," ",(0,n.Y)(I.I,{tooltip:(0,s.t)("End date excluded from time range"),placement:"right"})]}),(0,n.Y)(u.A,{ariaLabel:(0,s.t)("End (exclusive)"),options:A.OP,value:h,onChange:e=>f("untilMode",e)}),"specific"===h&&(0,n.Y)(k.A,{children:(0,n.Y)(L.l,{showTime:!0,defaultValue:(0,A.Ab)(c),onChange:e=>f("untilDatetime",e.format(A.c1)),allowClear:!1,getPopupContainer:t=>e.isOverflowingFilterBar?t.parentNode:document.body})}),"relative"===h&&(0,n.FD)(k.A,{gutter:8,children:[(0,n.Y)(O.A,{span:11,children:(0,n.Y)(M.A,{placeholder:(0,s.t)("Relative quantity"),value:m,min:1,defaultValue:1,onChange:e=>C("untilGrainValue",e||1),onStep:e=>C("untilGrainValue",e||1)})}),(0,n.Y)(O.A,{span:13,children:(0,n.Y)(u.A,{ariaLabel:(0,s.t)("Relative period"),options:A.s6,value:p,onChange:e=>f("untilGrain",e)})})]})]})]}),"relative"===r&&"relative"===h&&(0,n.FD)("div",{className:"control-anchor-to",children:[(0,n.Y)("div",{className:"control-label",children:(0,s.t)("Anchor to")}),(0,n.FD)(k.A,{align:"middle",children:[(0,n.Y)(O.A,{children:(0,n.Y)(x.s.GroupWrapper,{options:[{value:"now",label:(0,s.t)("Now")},{value:"specific",label:(0,s.t)("Date/Time")}],onChange:function(a){const n=a.target.value;"now"===n?e.onChange((0,A.IS)({...t,anchorValue:"now",anchorMode:n})):e.onChange((0,A.IS)({...t,anchorValue:A.bd,anchorMode:n}))},defaultValue:"now",value:g})}),"now"!==g&&(0,n.Y)(O.A,{children:(0,n.Y)(L.l,{showTime:!0,defaultValue:(0,A.Ab)(v),onChange:e=>f("anchorValue",e.format(A.c1)),allowClear:!1,className:"control-anchor-to-datetime",getPopupContainer:t=>e.isOverflowingFilterBar?t.parentNode:document.body})})]})]})]})})}var V=a(17355);const P=(0,n.FD)(n.FK,{children:[(0,n.FD)("div",{children:[(0,n.Y)("h3",{children:"DATETIME"}),(0,n.Y)("p",{children:(0,s.t)("Return to specific datetime.")}),(0,n.Y)("h4",{children:(0,s.t)("Syntax")}),(0,n.Y)("pre",{children:(0,n.Y)("code",{children:"datetime([string])"})}),(0,n.Y)("h4",{children:(0,s.t)("Example")}),(0,n.Y)("pre",{children:(0,n.Y)("code",{children:'datetime("2020-03-01 12:00:00")\ndatetime("now")\ndatetime("last year")'})})]}),(0,n.FD)("div",{children:[(0,n.Y)("h3",{children:"DATEADD"}),(0,n.Y)("p",{children:(0,s.t)("Moves the given set of dates by a specified interval.")}),(0,n.Y)("h4",{children:(0,s.t)("Syntax")}),(0,n.Y)("pre",{children:(0,n.Y)("code",{children:"dateadd([datetime], [integer], [dateunit])\ndateunit = (year | quarter | month | week | day | hour | minute | second)"})}),(0,n.Y)("h4",{children:(0,s.t)("Example")}),(0,n.Y)("pre",{children:(0,n.Y)("code",{children:'dateadd(datetime("today"), -13, day)\ndateadd(datetime("2020-03-01"), 2, day)'})})]}),(0,n.FD)("div",{children:[(0,n.Y)("h3",{children:"DATETRUNC"}),(0,n.Y)("p",{children:(0,s.t)("Truncates the specified date to the accuracy specified by the date unit.")}),(0,n.Y)("h4",{children:(0,s.t)("Syntax")}),(0,n.Y)("pre",{children:(0,n.Y)("code",{children:"datetrunc([datetime], [dateunit])\ndateunit = (year | quarter | month | week)"})}),(0,n.Y)("h4",{children:(0,s.t)("Example")}),(0,n.Y)("pre",{children:(0,n.Y)("code",{children:'datetrunc(datetime("2020-03-01"), week)\ndatetrunc(datetime("2020-03-01"), month)'})})]}),(0,n.FD)("div",{children:[(0,n.Y)("h3",{children:"LASTDAY"}),(0,n.Y)("p",{children:(0,s.t)("Get the last date by the date unit.")}),(0,n.Y)("h4",{children:(0,s.t)("Syntax")}),(0,n.Y)("pre",{children:(0,n.Y)("code",{children:"lastday([datetime], [dateunit])\ndateunit = (year | month | week)"})}),(0,n.Y)("h4",{children:(0,s.t)("Example")}),(0,n.Y)("pre",{children:(0,n.Y)("code",{children:'lastday(datetime("today"), month)'})})]}),(0,n.FD)("div",{children:[(0,n.Y)("h3",{children:"HOLIDAY"}),(0,n.Y)("p",{children:(0,s.t)("Get the specify date for the holiday")}),(0,n.Y)("h4",{children:(0,s.t)("Syntax")}),(0,n.Y)("pre",{children:(0,n.Y)("code",{children:"holiday([string])\nholiday([holiday string], [datetime])\nholiday([holiday string], [datetime], [country name])"})}),(0,n.Y)("h4",{children:(0,s.t)("Example")}),(0,n.Y)("pre",{children:(0,n.Y)("code",{children:'holiday("new year")\nholiday("christmas", datetime("2019"))\nholiday("christmas", dateadd(datetime("2019"), 1, year))\nholiday("christmas", datetime("2 years ago"))\nholiday("Easter Monday", datetime("2019"), "UK")'})})]})]}),W=e=>{const t=(0,i.DP)();return(0,n.Y)(r.Z2,{children:({css:a})=>(0,n.Y)(v.m,{overlayClassName:a`
            .ant-tooltip-content {
              min-width: ${125*t.sizeUnit}px;
              max-height: 410px;
              overflow-y: scroll;

              .ant-tooltip-inner {
                max-width: ${125*t.sizeUnit}px;
                h3 {
                  font-size: ${t.fontSize}px;
                  font-weight: ${t.fontWeightStrong};
                }
                h4 {
                  font-size: ${t.fontSize}px;
                  font-weight: ${t.fontWeightStrong};
                }
                pre {
                  border: none;
                  text-align: left;
                  word-break: break-word;
                  font-size: ${t.fontSizeSM}px;
                }
              }
            }
          `,...e})})};function G(e){return(0,n.Y)(W,{title:P,...e})}function B(e){return e.includes(c.wv)?e:e.startsWith("Last")?[e,""].join(c.wv):e.startsWith("Next")?["",e].join(c.wv):c.wv}function H(e){const t=B(e.value||""),[a,l]=t.split(c.wv);function i(t,n){"since"===t?e.onChange(`${n}${c.wv}${l}`):e.onChange(`${a}${c.wv}${n}`)}return t!==e.value&&e.onChange(B(e.value||"")),(0,n.FD)(n.FK,{children:[(0,n.FD)("div",{className:"section-title",children:[(0,s.t)("Configure Advanced Time Range "),(0,n.Y)(G,{placement:"rightBottom",children:(0,n.Y)(C.F.InfoCircleOutlined,{})})]}),(0,n.FD)("div",{className:"control-label",children:[(0,s.t)("Start (inclusive)")," ",(0,n.Y)(I.I,{tooltip:(0,s.t)("Start date included in time range"),placement:"right"})]}),(0,n.Y)(V.A,{value:a,onChange:e=>i("since",e.target.value)},"since"),(0,n.FD)("div",{className:"control-label",children:[(0,s.t)("End (exclusive)")," ",(0,n.Y)(I.I,{tooltip:(0,s.t)("End date excluded from time range"),placement:"right"})]}),(0,n.Y)(V.A,{value:l,onChange:e=>i("until",e.target.value)},"until")]})}const q=i.I4.div`
  ${({theme:e,isActive:t,isPlaceholder:a})=>r.AH`
    height: ${8*e.sizeUnit}px;

    display: flex;
    align-items: center;
    flex-wrap: nowrap;

    padding: 0 ${3*e.sizeUnit}px;

    background-color: ${e.colorBgContainer};

    border: 1px solid ${t?e.colorPrimary:e.colorBorder};
    border-radius: ${e.borderRadius}px;

    cursor: pointer;

    transition: border-color 0.3s cubic-bezier(0.65, 0.05, 0.36, 1);
    :hover,
    :focus {
      border-color: ${e.colorPrimary};
    }

    .date-label-content {
      color: ${a?e.colorTextPlaceholder:e.colorText};
      overflow: hidden;
      text-overflow: ellipsis;
      min-width: 0;
      flex-shrink: 1;
      white-space: nowrap;
    }

    span[role='img'] {
      color: ${a?e.colorTextPlaceholder:e.colorText};
      margin-left: auto;
      padding-left: ${e.sizeUnit}px;

      & > span[role='img'] {
        line-height: 0;
      }
    }
  `}
`,U=(0,l.forwardRef)(((e,t)=>(0,n.FD)(q,{...e,tabIndex:0,role:"button",children:[(0,n.Y)("span",{id:`date-label-${e.name}`,className:"date-label-content",ref:t,children:"string"==typeof e.label?(0,s.t)(e.label):e.label}),(0,n.Y)(C.F.CalendarOutlined,{iconSize:"s"})]}))),K=(0,i.I4)(u.A)`
  width: 272px;
`,Z=i.I4.div`
  ${({theme:e})=>r.AH`
    .ant-row {
      margin-top: 8px;
    }

    .ant-picker {
      padding: 4px 17px 4px;
      border-radius: 4px;
    }

    .ant-divider-horizontal {
      margin: 16px 0;
    }

    .control-label {
      font-size: ${e.fontSizeSM}px;
      line-height: 16px;
      margin: 8px 0;
    }

    .section-title {
      font-style: normal;
      font-weight: ${e.fontWeightStrong};
      font-size: 15px;
      line-height: 24px;
      margin-bottom: 8px;
    }

    .control-anchor-to {
      margin-top: 16px;
    }

    .control-anchor-to-datetime {
      width: 217px;
    }

    .footer {
      text-align: right;
    }
  `}
`,_=i.I4.span`
  span {
    margin-right: ${({theme:e})=>2*e.sizeUnit}px;
    vertical-align: middle;
  }
  .text {
    vertical-align: middle;
  }
  .error {
    color: ${({theme:e})=>e.colorError};
  }
`,J=(e,t,a)=>e?(0,n.FD)("div",{children:[t&&(0,n.Y)("strong",{children:t}),a&&(0,n.Y)("div",{css:e=>r.AH`
            margin-top: ${e.sizeUnit}px;
          `,children:a})]}):a||null;function X(e){var t;const{name:a,onChange:r,onOpenPopover:u=Y.fZ,onClosePopover:x=Y.fZ,overlayStyle:F="Popover",isOverflowingFilterBar:E=!1}=e,T=(0,A.IM)(),N=null!=(t=e.value)?t:T,[k,O]=(0,l.useState)(N),[I,L]=(0,l.useState)(!1),M=(0,l.useMemo)((()=>(0,A.J5)(N)),[N]),[R,V]=(0,l.useState)(M),[P,W]=(0,l.useState)(N),[G,B]=(0,l.useState)(N),[q,X]=(0,l.useState)(!1),[j,Q]=(0,l.useState)(N),[ee,te]=(0,l.useState)(N),ae=(0,i.DP)(),[ne,le]=(0,o.A)();function ie(){B(N),V(M),L(!1),x()}(0,l.useEffect)((()=>{if(N===d.WC)return O(d.WC),te(null),void X(!0);(0,c.x9)(N).then((({value:e,error:t})=>{t?(Q(t||""),X(!1),te(N||null)):("Common"===M||"Calendar"===M||"Current"===M||"No filter"===M?(O(N),te(J(le,N,e))):(O(e||""),te(J(le,e,N))),X(!0)),W(N),Q(e||N)}))}),[M,le,ne,N]),(0,b.sv)((()=>{if(G===d.WC)return Q(d.WC),W(d.WC),void X(!0);P!==G&&(0,c.x9)(G).then((({value:e,error:t})=>{t?(Q(t||""),X(!1)):(Q(e||""),X(!0)),W(G)}))}),h.Y.SLOW_DEBOUNCE,[G]);const re=()=>{I?ie():(B(N),V(M),L(!0),u())},oe=(0,n.FD)(Z,{children:[(0,n.Y)("div",{className:"control-label",children:(0,s.t)("Range type")}),(0,n.Y)(K,{ariaLabel:(0,s.t)("Range type"),options:A.BJ,value:R,onChange:function(e){e===d.WC&&B(d.WC),V(e)}}),"No filter"!==R&&(0,n.Y)(p.c,{}),"Common"===R&&(0,n.Y)(D,{value:G,onChange:B}),"Calendar"===R&&(0,n.Y)(S,{value:G,onChange:B}),"Current"===R&&(0,n.Y)($,{value:G,onChange:B}),"Advanced"===R&&(0,n.Y)(H,{value:G,onChange:B}),"Custom"===R&&(0,n.Y)(z,{value:G,onChange:B,isOverflowingFilterBar:E}),"No filter"===R&&(0,n.Y)("div",{}),(0,n.Y)(p.c,{}),(0,n.FD)("div",{children:[(0,n.Y)("div",{className:"section-title",children:(0,s.t)("Actual time range")}),q&&(0,n.Y)("div",{children:"No filter"===j?(0,s.t)("No filter"):j}),!q&&(0,n.FD)(_,{className:"warning",children:[(0,n.Y)(C.F.ExclamationCircleOutlined,{iconColor:ae.colorError}),(0,n.Y)("span",{className:"text error",children:j})]})]}),(0,n.Y)(p.c,{}),(0,n.FD)("div",{className:"footer",children:[(0,n.Y)(m.$,{buttonStyle:"secondary",cta:!0,onClick:ie,children:(0,s.t)("CANCEL")},"cancel"),(0,n.Y)(m.$,{buttonStyle:"primary",cta:!0,disabled:!q,onClick:function(){r(G),L(!1),x()},children:(0,s.t)("APPLY")},"apply")]})]}),de=(0,n.Y)(w.A,{autoAdjustOverflow:!1,trigger:"click",placement:"right",content:oe,title:(0,n.FD)(_,{children:[(0,n.Y)(C.F.EditOutlined,{}),(0,n.Y)("span",{className:"text",children:(0,s.t)("Edit time range")})]}),defaultOpen:I,open:I,onOpenChange:re,overlayStyle:{width:"600px"},destroyTooltipOnHide:!0,getPopupContainer:e=>E?e.parentNode:document.body,overlayClassName:"time-range-popover",children:(0,n.Y)(v.m,{placement:"top",title:ee,children:(0,n.Y)(U,{name:a,"aria-labelledby":`filter-name-${e.name}`,"aria-describedby":`date-label-${e.name}`,label:k,isActive:I,isPlaceholder:k===d.WC,ref:ne})})}),ce=(0,n.FD)(n.FK,{children:[(0,n.Y)(v.m,{placement:"top",title:ee,children:(0,n.Y)(U,{name:a,"aria-labelledby":`filter-name-${e.name}`,"aria-describedby":`date-label-${e.name}`,onClick:re,label:k,isActive:I,isPlaceholder:k===d.WC,ref:ne})}),(0,n.Y)(g.aF,{title:(0,n.Y)(y.r,{className:"text",isEditMode:!0,title:(0,s.t)("Edit time range")}),name:(0,s.t)("Edit time range"),show:I,onHide:re,width:"600px",hideFooter:!0,zIndex:1030,children:oe})]});return(0,n.FD)(n.FK,{children:[(0,n.Y)(f.A,{...e}),"Modal"===F?ce:de]})}}}]);