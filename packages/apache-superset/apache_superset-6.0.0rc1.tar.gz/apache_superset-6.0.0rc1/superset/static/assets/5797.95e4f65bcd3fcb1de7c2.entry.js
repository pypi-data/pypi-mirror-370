"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[5797],{5797:(e,a,t)=>{t.d(a,{A:()=>ie});var n=t(38221),l=t.n(n),i=t(2445),r=t(96540),o=t(50290),s=t(17437),d=t(31296),c=t(85600),h=t(40372),u=t(62070),p=t(47152),m=t(16370),g=t(95018),b=t(89232),v=t(61574),_=t(71519),f=t(8558),y=t(42566),x=t(30777),Y=t(85923),S=t(62193),C=t.n(S),w=t(58561),A=t.n(w),F=t(61225),k=t(33231),D=t(1763),E=t(74098),N=t(79378),$=t(56914);const T=({version:e="unknownVersion",sha:a="unknownSHA",build:t="unknownBuild"})=>{const n=`https://apachesuperset.gateway.scarf.sh/pixel/0d3461e1-abb1-4691-a0aa-5ed50de66af0/${e}/${a}/${t}`;return(0,i.Y)("img",{referrerPolicy:"no-referrer-when-downgrade",src:n,width:0,height:0,alt:""})};var M=t(5376),z=t(90886),L=t(47305),P=t(11753),U=t(14180),I=t(71323),O=t(31780),q=t(53118);const H=o.I4.div`
  display: flex;
  align-items: center;

  & i {
    margin-right: ${({theme:e})=>2*e.sizeUnit}px;
  }

  & a {
    display: block;
    width: 150px;
    word-wrap: break-word;
    text-decoration: none;
  }
`;var R=t(60511);const V=(0,D.a)(),j=e=>s.AH`
  padding: ${1.5*e.sizeUnit}px ${4*e.sizeUnit}px
    ${4*e.sizeUnit}px ${7*e.sizeUnit}px;
  color: ${e.colorText};
  font-size: ${e.fontSizeSM}px;
  white-space: nowrap;
`,K=o.I4.div`
  display: flex;
  height: 100%;
  flex-direction: row;
  justify-content: ${({align:e})=>e};
  align-items: center;
  margin-right: ${({theme:e})=>e.sizeUnit}px;
`,B=o.I4.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
`,J=o.I4.a`
  padding-right: ${({theme:e})=>e.sizeUnit}px;
  padding-left: ${({theme:e})=>e.sizeUnit}px;
`,G=o.I4.div`
  ${({theme:e,disabled:a})=>s.AH`
    &&:hover {
      color: ${!a&&e.colorPrimary};
      cursor: ${a?"not-allowed":"pointer"};
    }
    ${a&&s.AH`
      color: ${e.colorTextDisabled};
    `}
  `}
`,Q=({align:e,settings:a,navbarRight:t,isFrontendRoute:n,environmentTag:l,setQuery:d})=>{const h=(0,o.DP)(),u=(0,F.d4)((e=>e.user)),p=(0,F.d4)((e=>{var a;return null==(a=e.dashboardInfo)?void 0:a.id})),m=u||{},{roles:b}=m,{CSV_EXTENSIONS:v,COLUMNAR_EXTENSIONS:x,EXCEL_EXTENSIONS:Y,ALLOWED_EXTENSIONS:S,HAS_GSHEETS_INSTALLED:w}=(0,F.d4)((e=>e.common.conf)),[k,D]=(0,r.useState)(!1),[Q,W]=(0,r.useState)(!1),[X,Z]=(0,r.useState)(!1),[ee,ae]=(0,r.useState)(!1),[te,ne]=(0,r.useState)(""),le=(0,z.L)("can_sqllab","Superset",b),ie=(0,z.L)("can_write","Dashboard",b),re=(0,z.L)("can_write","Chart",b),oe=(0,z.L)("can_write","Database",b),se=(0,z.L)("can_write","Dataset",b),{canUploadData:de,canUploadCSV:ce,canUploadColumnar:he,canUploadExcel:ue}=(0,I.c8)(b,v,x,Y,S),pe=le||re||ie,[me,ge]=(0,r.useState)(!1),[be,ve]=(0,r.useState)(!1),_e=(0,L.N6)(u),fe=me||_e,{setThemeMode:ye,themeMode:xe,clearLocalOverrides:Ye,hasDevOverride:Se,canSetMode:Ce,canDetectOSPreference:we}=(0,O.w)(),Ae=[{label:(0,E.t)("Data"),icon:(0,i.Y)(f.F.DatabaseOutlined,{}),childs:[{label:(0,E.t)("Connect database"),name:R.$.DbConnection,perm:oe&&!be},{label:(0,E.t)("Create dataset"),name:R.$.DatasetCreation,url:"/dataset/add/",perm:se&&be},{label:(0,E.t)("Connect Google Sheet"),name:R.$.GoogleSheets,perm:oe&&w},{label:(0,E.t)("Upload CSV to database"),name:R.$.CSVUpload,perm:ce&&fe,disable:_e&&!me},{label:(0,E.t)("Upload Excel to database"),name:R.$.ExcelUpload,perm:ue&&fe,disable:_e&&!me},{label:(0,E.t)("Upload Columnar file to database"),name:R.$.ColumnarUpload,perm:he&&fe,disable:_e&&!me}]},{label:(0,E.t)("SQL query"),url:"/sqllab?new=true",icon:(0,i.Y)(f.F.SearchOutlined,{}),perm:"can_sqllab",view:"Superset"},{label:(0,E.t)("Chart"),url:Number.isInteger(p)?`/chart/add?dashboard_id=${p}`:"/chart/add",icon:(0,i.Y)(f.F.BarChartOutlined,{}),perm:"can_write",view:"Chart"},{label:(0,E.t)("Dashboard"),url:"/dashboard/new",icon:(0,i.Y)(f.F.DashboardOutlined,{}),perm:"can_write",view:"Dashboard"}],Fe=()=>{N.A.get({endpoint:`/api/v1/database/?q=${A().encode({filters:[{col:"allow_file_upload",opr:"upload_is_enabled",value:!0}]})}`}).then((({json:e})=>{var a;const t=(null==e||null==(a=e.result)?void 0:a.filter((e=>{var a;return null==e||null==(a=e.engine_information)?void 0:a.supports_file_upload})))||[];ge((null==t?void 0:t.length)>=1)}))},ke=()=>{N.A.get({endpoint:`/api/v1/database/?q=${A().encode({filters:[{col:"database_name",opr:"neq",value:"examples"}]})}`}).then((({json:e})=>{ve(e.count>=1)}))};(0,r.useEffect)((()=>{de&&Fe()}),[de]),(0,r.useEffect)((()=>{(oe||se)&&ke()}),[oe,se]);const De=(0,E.t)("Enable 'Allow file uploads to database' in any database's settings"),Ee=e=>({key:e.name||e.label,label:e.disable?(0,i.Y)(G,{disabled:!0,children:(0,i.Y)(g.m,{placement:"top",title:De,children:e.label})}):e.url?(0,i.Y)(y.o.Link,{href:(0,M.A)(e.url),children:e.label}):e.label,disabled:e.disable}),Ne=V.get("navbar.right"),$e=V.get("navbar.right-menu.item.icon"),Te=()=>{localStorage.removeItem("redux")},Me=(({setThemeMode:e,themeMode:a,hasLocalOverride:t=!1,onClearLocalSettings:n,allowOSPreference:l=!0})=>{const s=(0,o.DP)(),d=a=>{e(a)},c=(0,r.useMemo)((()=>({[q.lJ.DEFAULT]:(0,i.Y)(f.F.SunOutlined,{}),[q.lJ.DARK]:(0,i.Y)(f.F.MoonOutlined,{}),[q.lG.SYSTEM]:(0,i.Y)(f.F.FormatPainterOutlined,{}),[q.lJ.COMPACT]:(0,i.Y)(f.F.CompressOutlined,{})})),[]),h=(0,r.useMemo)((()=>t?(0,i.Y)(f.F.FormatPainterOutlined,{style:{color:s.colorError}}):c[a]),[t,s.colorError,c,a]),u=[{key:q.lG.DEFAULT,label:(0,i.FD)(i.FK,{children:[(0,i.Y)(f.F.SunOutlined,{})," ",(0,E.t)("Light")]}),onClick:()=>d(q.lG.DEFAULT)},{key:q.lG.DARK,label:(0,i.FD)(i.FK,{children:[(0,i.Y)(f.F.MoonOutlined,{})," ",(0,E.t)("Dark")]}),onClick:()=>d(q.lG.DARK)},...l?[{key:q.lG.SYSTEM,label:(0,i.FD)(i.FK,{children:[(0,i.Y)(f.F.FormatPainterOutlined,{})," ",(0,E.t)("Match system")]}),onClick:()=>d(q.lG.SYSTEM)}]:[]],p=[{type:"group",label:(0,E.t)("Theme"),key:"theme-group",children:u}];return n&&t&&(p.push({type:"divider",key:"theme-divider"}),p.push({key:"clear-local",label:(0,i.FD)(i.FK,{children:[(0,i.Y)(f.F.ClearOutlined,{})," ",(0,E.t)("Clear local theme")]}),onClick:n})),{key:"theme-sub-menu",label:h,icon:(0,i.Y)(f.F.CaretDownOutlined,{iconSize:"xs"}),children:p}})({setThemeMode:ye,themeMode:xe,hasLocalOverride:Se(),onClearLocalSettings:Ye,allowOSPreference:we()}),ze=(({locale:e,languages:a})=>(0,r.useMemo)((()=>{const t=Object.keys(a).map((e=>({key:e,label:(0,i.FD)(H,{className:"f16",children:[(0,i.Y)("i",{className:`flag ${a[e].flag}`}),(0,i.Y)(y.o.Link,{href:a[e].url,children:a[e].name})]}),style:{whiteSpace:"normal",height:"auto"}})));return{key:"language-submenu",type:"submenu",label:(0,i.Y)("span",{className:"f16","aria-label":(0,E.t)("Languages"),children:(0,i.Y)("i",{className:`flag ${a[e].flag}`})}),icon:(0,i.Y)(f.F.CaretDownOutlined,{iconSize:"xs"}),children:t,popupClassName:"language-picker-popup"}}),[a,e]))({locale:t.locale||"en",languages:t.languages||{}}),Le=(0,r.useMemo)((()=>{const e=[];return Ne&&e.push({key:"extension",label:(0,i.Y)(Ne,{})}),!t.user_is_anonymous&&pe&&e.push({key:"new-dropdown",label:(0,i.Y)(f.F.PlusOutlined,{iconColor:h.colorPrimary}),icon:(0,i.Y)(f.F.CaretDownOutlined,{iconSize:"xs"}),children:(()=>{const e=[];return null==Ae||Ae.forEach((a=>{var t;const l=null==(t=a.childs)?void 0:t.some((e=>"object"==typeof e&&!!e.perm));if(a.childs)if(l){const t=[];a.childs.forEach(((e,a)=>{"string"!=typeof e&&e.name&&e.perm&&(3===a&&t.push({type:"divider",key:`divider-${a}`}),t.push(Ee(e)))})),e.push({key:`sub2_${a.label}`,label:a.label,icon:a.icon,children:t})}else a.url&&(0,z.L)(a.perm,a.view,b)&&e.push({key:a.label,label:n(a.url)?(0,i.FD)(_.N_,{to:a.url||"",children:[a.icon," ",a.label]}):(0,i.FD)(y.o.Link,{href:(0,M.A)(a.url||""),children:[a.icon," ",a.label]})});else(0,z.L)(a.perm,a.view,b)&&e.push({key:a.label,label:n(a.url)?(0,i.FD)(_.N_,{to:a.url||"",children:[a.icon," ",a.label]}):(0,i.FD)(y.o.Link,{href:(0,M.A)(a.url||""),children:[a.icon," ",a.label]})})})),e})()}),Ce()&&e.push(Me),t.show_language_picker&&ze&&e.push(ze),e.push({key:"settings",label:(0,E.t)("Settings"),icon:(0,i.Y)(f.F.CaretDownOutlined,{iconSize:"xs"}),children:(()=>{const e=[];if(null==a||a.forEach(((t,l)=>{var r;const o=[];null==(r=t.childs)||r.forEach((e=>{if("string"!=typeof e){const a=$e?(0,i.FD)(B,{children:[e.label,(0,i.Y)($e,{menuChild:e})]}):e.label;o.push({key:e.label,label:n(e.url)?(0,i.Y)(_.N_,{to:e.url||"",children:a}):(0,i.Y)(y.o.Link,{href:e.url||"",css:s.AH`
                    display: flex;
                    align-items: center;
                    line-height: ${10*h.sizeUnit}px;
                  `,children:a})})}})),e.push({type:"group",label:t.label,key:t.label,children:o}),l<a.length-1&&e.push({type:"divider",key:`divider_${l}`})})),!t.user_is_anonymous){e.push({type:"divider",key:"user-divider"});const a=[];t.user_info_url&&a.push({key:"info",label:(0,i.Y)(y.o.Link,{href:t.user_info_url,children:(0,E.t)("Info")})}),a.push({key:"logout",label:(0,i.Y)(y.o.Link,{href:t.user_logout_url,children:(0,E.t)("Logout")}),onClick:Te}),e.push({type:"group",label:(0,E.t)("User"),key:"user-section",children:a})}return(t.version_string||t.version_sha)&&(e.push({type:"divider",key:"version-info-divider"}),e.push({type:"group",label:(0,E.t)("About"),key:"about-section",children:[{key:"about-info",label:(0,i.FD)("div",{className:"about-section",children:[t.show_watermark&&(0,i.Y)("div",{css:j,children:(0,E.t)("Powered by Apache Superset")}),t.version_string&&(0,i.FD)("div",{css:j,children:[(0,E.t)("Version"),": ",t.version_string]}),t.version_sha&&(0,i.FD)("div",{css:j,children:[(0,E.t)("SHA"),": ",t.version_sha]}),t.build_number&&(0,i.FD)("div",{css:j,children:[(0,E.t)("Build"),": ",t.build_number]})]})}]})),e})()}),e}),[Ne,t,pe,Ce,h.colorPrimary,Me,ze,Ae,b,a,$e,Ee,Te]);return(0,i.FD)(K,{align:e,children:[oe&&(0,i.Y)(P.Ay,{onHide:()=>{ne(""),D(!1)},show:k,dbEngine:te,onDatabaseAdd:()=>d({databaseAdded:!0})}),ce&&(0,i.Y)(U.A,{onHide:()=>W(!1),show:Q,allowedExtensions:v,type:"csv"}),ue&&(0,i.Y)(U.A,{onHide:()=>Z(!1),show:X,allowedExtensions:Y,type:"excel"}),he&&(0,i.Y)(U.A,{onHide:()=>ae(!1),show:ee,allowedExtensions:x,type:"columnar"}),(null==l?void 0:l.text)&&(()=>{const e=["error","warning","success","processing","default"].includes(l.color)?l.color:"default";return(0,i.Y)($.A,{color:e,css:s.AH`
                border-radius: ${125*h.sizeUnit}px;
              `,children:l.text})})(),(0,i.Y)(c.W1,{css:s.AH`
          display: flex;
          flex-direction: row;
          align-items: center;
        `,selectable:!1,mode:"horizontal",onClick:e=>{e.key===R.$.DbConnection?D(!0):e.key===R.$.GoogleSheets?(D(!0),ne("Google Sheets")):e.key===R.$.CSVUpload?W(!0):e.key===R.$.ExcelUpload?Z(!0):e.key===R.$.ColumnarUpload&&ae(!0)},onOpenChange:e=>(e.length>1&&!C()(null==e?void 0:e.filter((e=>{var a;return e.includes(`sub2_${null==Ae||null==(a=Ae[0])?void 0:a.label}`)})))&&(de&&Fe(),(oe||se)&&ke()),null),disabledOverflow:!0,items:Le}),t.documentation_url&&(0,i.FD)(i.FK,{children:[(0,i.Y)(J,{href:t.documentation_url,target:"_blank",rel:"noreferrer",title:t.documentation_text||(0,E.t)("Documentation"),children:t.documentation_icon?(0,i.Y)(f.F.BookOutlined,{}):(0,i.Y)(f.F.QuestionCircleOutlined,{})}),(0,i.Y)("span",{children:" "})]}),t.bug_report_url&&(0,i.FD)(i.FK,{children:[(0,i.Y)(J,{href:t.bug_report_url,target:"_blank",rel:"noreferrer",title:t.bug_report_text||(0,E.t)("Report a bug"),children:t.bug_report_icon?(0,i.Y)("i",{className:t.bug_report_icon}):(0,i.Y)(f.F.BugOutlined,{})}),(0,i.Y)("span",{children:" "})]}),t.user_is_anonymous&&(0,i.FD)(J,{href:t.user_login_url,children:[(0,i.Y)(f.F.LoginOutlined,{})," ",(0,E.t)("Login")]}),(0,i.Y)(T,{version:t.version_string,sha:t.version_sha,build:t.build_number})]})},W=e=>{const[,a]=(0,k.sq)({databaseAdded:k.sJ,datasetAdded:k.sJ});return(0,i.Y)(Q,{setQuery:a,...e})};class X extends r.PureComponent{constructor(...e){super(...e),this.state={hasError:!1},this.noop=()=>{}}static getDerivedStateFromError(){return{hasError:!0}}render(){return this.state.hasError?(0,i.Y)(Q,{setQuery:this.noop,...this.props}):this.props.children}}const Z=e=>(0,i.Y)(X,{...e,children:(0,i.Y)(W,{...e})}),ee=o.I4.header`
  ${({theme:e})=>`\n      background-color: ${e.colorBgContainer};\n      border-bottom: 1px solid ${e.colorBorderSecondary};\n      z-index: 10;\n\n      &:nth-last-of-type(2) nav {\n        margin-bottom: 2px;\n      }\n      .caret {\n        display: none;\n      }\n      & .ant-image{\n        display: contents;\n        height: 100%;\n        padding: ${e.sizeUnit}px\n          ${2*e.sizeUnit}px\n          ${e.sizeUnit}px\n          ${4*e.sizeUnit}px;\n      }\n      .navbar-brand {\n        display: flex;\n        flex-direction: column;\n        justify-content: center;\n        /* must be exactly the height of the Antd navbar */\n        min-height: 50px;\n        padding: ${e.sizeUnit}px\n          ${2*e.sizeUnit}px\n          ${e.sizeUnit}px\n          ${4*e.sizeUnit}px;\n        max-width: ${e.sizeUnit*e.brandIconMaxWidth}px;\n        img {\n          height: 100%;\n          object-fit: contain;\n        }\n        &:focus {\n          border-color: transparent;\n        }\n        &:focus-visible {\n          border-color: ${e.colorPrimaryText};\n        }\n      }\n      .navbar-brand-text {\n        border-left: 1px solid ${e.colorBorderSecondary};\n        border-right: 1px solid ${e.colorBorderSecondary};\n        height: 100%;\n        color: ${e.colorText};\n        padding-left: ${4*e.sizeUnit}px;\n        padding-right: ${4*e.sizeUnit}px;\n        margin-right: ${6*e.sizeUnit}px;\n        font-size: ${e.fontSizeLG}px;\n        float: left;\n        display: flex;\n        flex-direction: column;\n        justify-content: center;\n\n        span {\n          max-width: ${58*e.sizeUnit}px;\n          white-space: nowrap;\n          overflow: hidden;\n          text-overflow: ellipsis;\n        }\n        @media (max-width: 1127px) {\n          display: none;\n        }\n      }\n      @media (max-width: 767px) {\n        .navbar-brand {\n          float: none;\n        }\n      }\n      @media (max-width: 767px) {\n        .ant-menu-item {\n          padding: 0 ${6*e.sizeUnit}px 0\n            ${3*e.sizeUnit}px !important;\n        }\n        .ant-menu > .ant-menu-item > span > a {\n          padding: 0px;\n        }\n        .main-nav .ant-menu-submenu-title > svg:nth-of-type(1) {\n          display: none;\n        }\n      }\n  `}
`,{SubMenu:ae}=c.NG,te=(0,o.I4)(ae)`
  ${({theme:e})=>s.AH`
    [data-icon="caret-down"] {
      color: ${e.colorIcon};
      font-size: ${e.fontSizeXS}px;
      margin-left: ${e.sizeUnit}px;
    }
    &.ant-menu-submenu {
        padding: ${2*e.sizeUnit}px ${4*e.sizeUnit}px;
        display: flex;
        align-items: center;
        height: 100%;  &.ant-menu-submenu-active {
    .ant-menu-title-content {
      color: ${e.colorPrimary};
    }
  }
  `}
`,{useBreakpoint:ne}=h.Ay;function le({data:{menu:e,brand:a,navbar_right:t,settings:n,environment_tag:s},isFrontendRoute:h=()=>!1}){const[S,C]=(0,r.useState)("horizontal"),w=ne(),A=(0,x.Q1)(),F=(0,o.DP)();let k;(0,r.useEffect)((()=>{function e(){window.innerWidth<=767?C("inline"):C("horizontal")}e();const a=l()((()=>e()),10);return window.addEventListener("resize",a),()=>window.removeEventListener("resize",a)}),[]),function(e){e.Explore="/explore",e.Dashboard="/dashboard",e.Chart="/chart",e.Datasets="/tablemodelview"}(k||(k={}));const D=[],[E,N]=(0,r.useState)(D),$=(0,v.zy)();return(0,r.useEffect)((()=>{const e=$.pathname;switch(!0){case e.startsWith(k.Dashboard):N(["Dashboards"]);break;case e.startsWith(k.Chart)||e.startsWith(k.Explore):N(["Charts"]);break;case e.startsWith(k.Datasets):N(["Datasets"]);break;default:N(D)}}),[$.pathname]),(0,d.P3)(Y.vX.standalone)||A.hideNav?(0,i.Y)(i.FK,{}):(0,i.Y)(ee,{className:"top",id:"main-menu",role:"navigation",children:(0,i.FD)(p.A,{children:[(0,i.FD)(m.A,{md:16,xs:24,style:{display:"flex"},children:[(0,i.Y)(g.m,{id:"brand-tooltip",placement:"bottomLeft",title:a.tooltip,arrow:{pointAtCenter:!0},children:(()=>{let e;if(F.brandLogoUrl){let a={padding:"0px",margin:"0px"};F.brandLogoHeight&&(a={...a,height:F.brandLogoHeight,minHeight:"0px"}),F.brandLogoMargin&&(a={...a,margin:F.brandLogoMargin}),e=(0,i.Y)(y.o.Link,{href:F.brandLogoHref,className:"navbar-brand",style:a,children:(0,i.Y)(u.A,{preview:!1,src:F.brandLogoUrl,alt:F.brandLogoAlt||"Apache Superset"})})}else e=h(window.location.pathname)?(0,i.Y)(b.Kt,{className:"navbar-brand",to:a.path,children:(0,i.Y)(u.A,{preview:!1,src:a.icon,alt:a.alt})}):(0,i.Y)(y.o.Link,{className:"navbar-brand",href:a.path,tabIndex:-1,children:(0,i.Y)(u.A,{preview:!1,src:a.icon,alt:a.alt})});return(0,i.Y)(i.FK,{children:e})})()}),a.text&&(0,i.Y)("div",{className:"navbar-brand-text",children:(0,i.Y)("span",{children:a.text})}),(0,i.Y)(c.NG,{mode:S,className:"main-nav",selectedKeys:E,disabledOverflow:!0,children:e.map(((e,a)=>{var t;return(({label:e,childs:a,url:t,index:n,isFrontendRoute:l})=>t&&l?(0,i.Y)(c.NG.Item,{role:"presentation",children:(0,i.Y)(_.k2,{role:"button",to:t,activeClassName:"is-active",children:e})},e):t?(0,i.Y)(c.NG.Item,{children:(0,i.Y)(y.o.Link,{href:t,children:e})},e):(0,i.Y)(te,{title:e,icon:"inline"===S?(0,i.Y)(i.FK,{}):(0,i.Y)(f.F.CaretDownOutlined,{iconSize:"xs"}),children:null==a?void 0:a.map(((a,t)=>"string"==typeof a&&"-"===a&&"Data"!==e?(0,i.Y)(c.NG.Divider,{},`$${t}`):"string"!=typeof a?(0,i.Y)(c.NG.Item,{children:a.isFrontendRoute?(0,i.Y)(_.k2,{to:a.url||"",exact:!0,activeClassName:"is-active",children:a.label}):(0,i.Y)(y.o.Link,{href:a.url,children:a.label})},`${a.label}`):null))},n))({index:a,...e,isFrontendRoute:h(e.url),childs:null==(t=e.childs)?void 0:t.map((e=>"string"==typeof e?e:{...e,isFrontendRoute:h(e.url)}))})}))})]}),(0,i.Y)(m.A,{md:8,xs:24,children:(0,i.Y)(Z,{align:w.md?"flex-end":"flex-start",settings:n,navbarRight:t,isFrontendRoute:h,environmentTag:s})})]})})}function ie({data:e,...a}){const t={...e},n={Data:!0,Security:!0,Manage:!0},l=[],r=[];return t.menu.forEach((e=>{if(!e)return;const a=[],t={...e};e.childs&&(e.childs.forEach((e=>{("string"==typeof e||e.label)&&a.push(e)})),t.childs=a),n.hasOwnProperty(e.name)?r.push(t):l.push(t)})),t.menu=l,t.settings=r,(0,i.Y)(le,{data:t,...a})}},11753:(e,a,t)=>{t.d(a,{hT:()=>ta,Ay:()=>ra});var n=t(44383),l=t.n(n),i=t(62193),r=t.n(i),o=t(2445),s=t(1763),d=t(50290),c=t(74098),h=t(96540),u=t(61574),p=t(24777),m=t(21325),g=t(23195),b=t(2801),v=t(94185),_=t(17437),f=t(42566),y=t(8558),x=t(4651),Y=t(95018);const S=({buttonText:e,icon:a,altText:t,...n})=>(0,o.Y)(x.Z,{hoverable:!0,role:"button",tabIndex:0,"aria-label":e,onKeyDown:e=>{"Enter"!==e.key&&" "!==e.key||(n.onClick&&n.onClick(e)," "===e.key&&e.preventDefault()),null==n.onKeyDown||n.onKeyDown(e)},cover:a?(0,o.Y)("img",{src:a,alt:t||e,css:_.AH`
          width: 100%;
          object-fit: contain;
          height: 100px;
        `}):(0,o.Y)("div",{css:_.AH`
          display: flex;
          align-content: center;
          align-items: center;
          height: 100px;
        `,children:(0,o.Y)(y.F.DatabaseOutlined,{css:_.AH`
            font-size: 48px;
          `,"aria-label":"default-icon"})}),css:e=>({padding:3*e.sizeUnit,textAlign:"center",...n.style}),...n,children:(0,o.Y)(Y.m,{title:e,children:(0,o.Y)(f.o.Text,{ellipsis:!0,children:e})})});var C,w,A=t(32202),F=t(88217),k=t(97163),D=t(5250),E=t(77829),N=t(92998),$=t(89232),T=t(64457),M=t(86784),z=t(46720),L=t(51692);!function(e){e.SqlalchemyUri="sqlalchemy_form",e.DynamicForm="dynamic_form"}(C||(C={})),function(e){e.GSheet="gsheets",e.BigQuery="bigquery",e.Snowflake="snowflake"}(w||(w={}));var P=t(46942),U=t.n(P),I=t(99106),O=t(43303),q=t(64917),H=t(91196),R=t(17355),V=t(45207),j=t(52167);const K=_.AH`
  margin-bottom: 0;
`,B=d.I4.header`
  padding: ${({theme:e})=>2*e.sizeUnit}px
    ${({theme:e})=>4*e.sizeUnit}px;
  line-height: ${({theme:e})=>6*e.sizeUnit}px;

  .helper-top {
    padding-bottom: 0;
    color: ${({theme:e})=>e.colorText};
    font-size: ${({theme:e})=>e.fontSizeSM}px;
    margin: 0;
  }

  .subheader-text {
    line-height: ${({theme:e})=>4.25*e.sizeUnit}px;
  }

  .helper-bottom {
    padding-top: 0;
    color: ${({theme:e})=>e.colorText};
    font-size: ${({theme:e})=>e.fontSizeSM}px;
    margin: 0;
  }

  h4 {
    color: ${({theme:e})=>e.colorText};
    font-size: ${({theme:e})=>e.fontSizeLG}px;
    margin: 0;
    padding: 0;
    line-height: ${({theme:e})=>8*e.sizeUnit}px;
  }

  .select-db {
    padding-bottom: ${({theme:e})=>2*e.sizeUnit}px;
    .helper {
      margin: 0;
    }

    h4 {
      margin: 0 0 ${({theme:e})=>4*e.sizeUnit}px;
    }
  }
`,J=_.AH`
  .ant-tabs-top {
    margin-top: 0;
  }
  .ant-tabs-top > .ant-tabs-nav {
    margin-bottom: 0;
  }
  .ant-tabs-tab {
    margin-right: 0;
  }
`,G=_.AH`
  .ant-modal-body {
    padding-left: 0;
    padding-right: 0;
    padding-top: 0;
  }
`,Q=e=>_.AH`
  margin-bottom: ${5*e.sizeUnit}px;
  svg {
    margin-bottom: ${.25*e.sizeUnit}px;
  }
  display: flex;
`,W=e=>_.AH`
  padding-left: ${2*e.sizeUnit}px;
  padding-right: ${2*e.sizeUnit}px;
`,X=e=>_.AH`
  padding: ${4*e.sizeUnit}px ${4*e.sizeUnit}px 0;
`,Z=e=>_.AH`
  .ant-select-dropdown {
    height: ${40*e.sizeUnit}px;
  }

  .ant-modal-header {
    padding: ${4.5*e.sizeUnit}px ${4*e.sizeUnit}px
      ${4*e.sizeUnit}px;
  }

  .ant-modal-close-x .close {
    opacity: 1;
  }

  .ant-modal-body {
    height: ${180.5*e.sizeUnit}px;
  }

  .ant-modal-footer {
    height: ${16.25*e.sizeUnit}px;
  }
`,ee=e=>_.AH`
  margin: ${4*e.sizeUnit}px 0;
`,ae=d.I4.div`
  ${({theme:e})=>_.AH`
    margin: 0 ${4*e.sizeUnit}px ${4*e.sizeUnit}px;
  `}
`,te=e=>_.AH`
  .required {
    margin-left: ${e.sizeUnit/2}px;
    color: ${e.colorError};
  }

  .helper {
    display: block;
    padding: ${e.sizeUnit}px 0;
    color: ${e.colorTextSecondary};
    font-size: ${e.fontSizeSM}px;
    text-align: left;
  }
`,ne=e=>_.AH`
  .form-group {
    margin-bottom: ${4*e.sizeUnit}px;
    &-w-50 {
      display: inline-block;
      width: ${`calc(50% - ${4*e.sizeUnit}px)`};
      & + .form-group-w-50 {
        margin-left: ${8*e.sizeUnit}px;
      }
    }
  }
  .helper {
    color: ${e.colorTextSecondary};
    font-size: ${e.fontSizeSM}px;
    margin-top: ${1.5*e.sizeUnit}px;
  }
  .ant-tabs-content-holder {
    overflow: auto;
    max-height: 480px;
  }
`,le=e=>_.AH`
  label {
    color: ${e.colorText};
    font-size: ${e.fontSizeSM}px;
    margin-bottom: 0;
  }
`,ie=d.I4.div`
  ${({theme:e})=>_.AH`
    margin-bottom: ${6*e.sizeUnit}px;
    &.mb-0 {
      margin-bottom: 0;
    }
    &.mb-8 {
      margin-bottom: ${2*e.sizeUnit}px;
    }

    &.extra-container {
      padding-top: ${2*e.sizeUnit}px;
    }

    .input-container {
      display: flex;
      align-items: top;

      label {
        display: flex;
        margin-left: ${2*e.sizeUnit}px;
        margin-top: ${.75*e.sizeUnit}px;
        font-family: ${e.fontFamily};
        font-size: ${e.fontSize}px;
      }

      i {
        margin: 0 ${e.sizeUnit}px;
      }
    }

    input,
    textarea {
      flex: 1 1 auto;
    }

    textarea {
      height: 160px;
      resize: none;
    }

    input::placeholder,
    textarea::placeholder {
      color: ${e.colorTextPlaceholder};
    }

    textarea,
    input[type='text'],
    input[type='number'] {
      padding: ${1.5*e.sizeUnit}px ${2*e.sizeUnit}px;
      border-style: none;
      border: 1px solid ${e.colorBorder};
      border-radius: ${e.borderRadius}px;

      &[name='name'] {
        flex: 0 1 auto;
        width: 40%;
      }
    }
    &.expandable {
      height: 0;
      overflow: hidden;
      transition: height 0.25s;
      margin-left: ${8*e.sizeUnit}px;
      margin-bottom: 0;
      padding: 0;
      &.open {
        height: ${108}px;
        padding-right: ${5*e.sizeUnit}px;
      }
    }
  `}
`,re=(0,d.I4)(j.iN)`
  flex: 1 1 auto;
  /* Border is already applied by AceEditor itself */
`,oe=d.I4.div`
  padding-top: ${({theme:e})=>e.sizeUnit}px;
  .input-container {
    padding-top: ${({theme:e})=>e.sizeUnit}px;
    padding-bottom: ${({theme:e})=>e.sizeUnit}px;
  }
  &.expandable {
    height: 0;
    overflow: hidden;
    transition: height 0.25s;
    margin-left: ${({theme:e})=>7*e.sizeUnit}px;
    &.open {
      height: ${261}px;
      &.ctas-open {
        height: ${363}px;
      }
    }
  }
`,se=d.I4.div`
  padding: 0 ${({theme:e})=>4*e.sizeUnit}px;
  margin-top: ${({theme:e})=>6*e.sizeUnit}px;
`,de=e=>_.AH`
  text-transform: initial;
  padding-right: ${2*e.sizeUnit}px;
`,ce=e=>_.AH`
  font-size: ${3.5*e.sizeUnit}px;
  text-transform: initial;
  padding-right: ${2*e.sizeUnit}px;
`,he=d.I4.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0px;

  .helper {
    color: ${({theme:e})=>e.colorTextSecondary};
    font-size: ${({theme:e})=>e.fontSizeSM}px;
    margin: 0px;
  }
`,ue=(d.I4.div`
  color: ${({theme:e})=>e.colorText};
  font-weight: ${({theme:e})=>e.fontWeightStrong};
  font-size: ${({theme:e})=>e.fontSize}px;
`,d.I4.div`
  color: ${({theme:e})=>e.colorText};
  font-size: ${({theme:e})=>e.fontSizeSM}px;
`,d.I4.div`
  color: ${({theme:e})=>e.colorTextSecondary};
  font-size: ${({theme:e})=>e.fontSizeSM}px;
`),pe=d.I4.div`
  color: ${({theme:e})=>e.colorText};
  font-size: ${({theme:e})=>e.fontSizeLG}px;
  font-weight: ${({theme:e})=>e.fontWeightStrong};
`,me=d.I4.div`
  .catalog-type-select {
    margin: 0 0 20px;
  }

  .label-select {
    color: ${({theme:e})=>e.colorText};
    font-size: 11px;
    margin: 0 5px ${({theme:e})=>2*e.sizeUnit}px;
  }

  .label-paste {
    color: ${({theme:e})=>e.colorTextSecondary};
    font-size: 11px;
    line-height: 16px;
  }

  .input-container {
    margin: ${({theme:e})=>4*e.sizeUnit}px 0;
    display: flex;
    flex-direction: column;
}
  }
  .input-form {
    height: 100px;
    width: 100%;
    border: 1px solid ${({theme:e})=>e.colorBorder};
    border-radius: ${({theme:e})=>e.borderRadius}px;
    resize: vertical;
    padding: ${({theme:e})=>1.5*e.sizeUnit}px
      ${({theme:e})=>2*e.sizeUnit}px;
    &::placeholder {
      color: ${({theme:e})=>e.colorTextPlaceholder};
    }
  }

  .input-container {
    width: 100%;

    button {
      width: fit-content;
    }

    .credentials-uploaded {
      display: flex;
      align-items: center;
      gap: ${({theme:e})=>3*e.sizeUnit}px;
      width: fit-content;
    }

    .credentials-uploaded-btn, .credentials-uploaded-remove {
      flex: 0 0 auto;
    }

    /* hide native file upload input element */
    .input-upload {
      display: none !important;
    }
  }`,ge=d.I4.div`
  .preferred {
    .superset-button {
      margin-left: 0;
    }
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    margin: ${({theme:e})=>4*e.sizeUnit}px;
  }

  .preferred-item {
    width: 32%;
    margin-bottom: ${({theme:e})=>2.5*e.sizeUnit}px;
  }

  .available {
    margin: ${({theme:e})=>4*e.sizeUnit}px;
    .available-label {
      font-size: ${({theme:e})=>e.fontSizeLG}px;
      font-weight: ${({theme:e})=>e.fontWeightStrong};
      margin: ${({theme:e})=>6*e.sizeUnit}px 0;
    }
    .available-select {
      width: 100%;
    }
  }

  .label-available-select {
    font-size: ${({theme:e})=>e.fontSizeSM}px;
  }
`,be=(0,d.I4)(F.$)`
  width: ${({theme:e})=>40*e.sizeUnit}px;
`,ve=d.I4.div`
  position: sticky;
  top: 0;
  z-index: ${({theme:e})=>e.zIndexPopupBase};
  background: ${({theme:e})=>e.colorBgLayout};
  height: auto;
`,_e=d.I4.div`
  margin-bottom: 16px;

  .catalog-type-select {
    margin: 0 0 20px;
  }

  .gsheet-title {
    font-size: ${({theme:e})=>e.fontSizeLG}px;
    font-weight: ${({theme:e})=>e.fontWeightStrong};
    margin: ${({theme:e})=>10*e.sizeUnit}px 0 16px;
  }

  .catalog-label {
    margin: 0 0 7px;
  }

  .catalog-name {
    display: flex;
    .catalog-name-input {
      width: 95%;
      margin-bottom: 0px;
    }
  }

  .catalog-name-url {
    margin: 4px 0;
    width: 95%;
  }

  .catalog-add-btn {
    width: 95%;
  }
`,fe=d.I4.div`
  margin: ${({theme:e})=>4*e.sizeUnit}px;
  .ant-progress-inner {
    display: none;
  }

  .ant-upload-list-item-card-actions {
    display: none;
  }
`,ye=({db:e,onInputChange:a,onTextChange:t,onEditorChange:n,onExtraInputChange:l,onExtraEditorChange:i,extraExtension:r})=>{var s,u,p,m,g;const b=!(null==e||!e.expose_in_sqllab),v=!!(null!=e&&e.allow_ctas||null!=e&&e.allow_cvas),_=null==e||null==(s=e.engine_information)?void 0:s.supports_file_upload,f=null==e||null==(u=e.engine_information)?void 0:u.supports_dynamic_catalog,y=JSON.parse((null==e?void 0:e.extra)||"{}",((e,a)=>"engine_params"===e&&"object"==typeof a?JSON.stringify(a):a)),x=(0,V.p)(null==e?void 0:e.masked_encrypted_extra,{errorPrefix:"Invalid secure extra JSON"}),Y=Object.keys((null==y?void 0:y.metadata_params)||{}).length?"string"==typeof(null==y?void 0:y.metadata_params)?null==y?void 0:y.metadata_params:JSON.stringify(null==y?void 0:y.metadata_params):"",S=(0,V.p)(Y,{errorPrefix:"Invalid metadata parameters JSON"}),C=Object.keys((null==y?void 0:y.engine_params)||{}).length?"string"==typeof(null==y?void 0:y.engine_params)?null==y?void 0:y.engine_params:JSON.stringify(null==y?void 0:y.engine_params):"",w=(0,V.p)(C,{errorPrefix:"Invalid engine parameters JSON"}),A=(0,d.DP)(),F=null==r?void 0:r.component,k=null==r?void 0:r.logo,E=null==r?void 0:r.description,N=!!(0,I.G7)(I.TO.ForceSqlLabRunAsync)||!(null==e||!e.allow_run_async),$=(0,I.G7)(I.TO.ForceSqlLabRunAsync),[T,M]=(0,h.useState)();return(0,h.useEffect)((()=>{b||void 0===T||M(void 0)}),[b]),(0,o.Y)(O.S,{expandIconPosition:"end",accordion:!0,modalMode:!0,activeKey:T,onChange:e=>M(e),items:[{key:"sql-lab",label:(0,o.Y)(q.s,{title:(0,c.t)("SQL Lab"),subtitle:(0,c.t)("Adjust how this database will interact with SQL Lab."),testId:"sql-lab-label-test"}),children:(0,o.Y)(o.FK,{children:(0,o.FD)(ie,{css:K,children:[(0,o.FD)("div",{className:"input-container",children:[(0,o.Y)(H.A,{id:"expose_in_sqllab",name:"expose_in_sqllab",indeterminate:!1,checked:!(null==e||!e.expose_in_sqllab),onChange:a,children:(0,c.t)("Expose database in SQL Lab")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("Allow this database to be queried in SQL Lab")})]}),(0,o.FD)(oe,{className:U()("expandable",{open:b,"ctas-open":v}),children:[(0,o.Y)(ie,{css:K,children:(0,o.FD)("div",{className:"input-container",children:[(0,o.Y)(H.A,{id:"allow_ctas",name:"allow_ctas",indeterminate:!1,checked:!(null==e||!e.allow_ctas),onChange:a,children:(0,c.t)("Allow CREATE TABLE AS")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("Allow creation of new tables based on queries")})]})}),(0,o.FD)(ie,{css:K,children:[(0,o.FD)("div",{className:"input-container",children:[(0,o.Y)(H.A,{id:"allow_cvas",name:"allow_cvas",indeterminate:!1,checked:!(null==e||!e.allow_cvas),onChange:a,children:(0,c.t)("Allow CREATE VIEW AS")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("Allow creation of new views based on queries")})]}),(0,o.FD)(ie,{className:U()("expandable",{open:v}),children:[(0,o.Y)("div",{className:"control-label",children:(0,c.t)("CTAS & CVAS SCHEMA")}),(0,o.Y)("div",{className:"input-container",children:(0,o.Y)(R.A,{type:"text",name:"force_ctas_schema",placeholder:(0,c.t)("Create or select schema..."),onChange:a,value:(null==e?void 0:e.force_ctas_schema)||""})}),(0,o.Y)("div",{className:"helper",children:(0,c.t)("Force all tables and views to be created in this schema when clicking CTAS or CVAS in SQL Lab.")})]})]}),(0,o.Y)(ie,{css:K,children:(0,o.FD)("div",{className:"input-container",children:[(0,o.Y)(H.A,{id:"allow_dml",name:"allow_dml",indeterminate:!1,checked:!(null==e||!e.allow_dml),onChange:a,children:(0,c.t)("Allow DDL and DML")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("Allow the execution of DDL (Data Definition Language: CREATE, DROP, TRUNCATE, etc.) and DML (Data Modification Language: INSERT, UPDATE, DELETE, etc)")})]})}),(0,o.Y)(ie,{css:K,children:(0,o.FD)("div",{className:"input-container",children:[(0,o.Y)(H.A,{id:"cost_estimate_enabled",name:"cost_estimate_enabled",indeterminate:!1,checked:!(null==y||!y.cost_estimate_enabled),onChange:l,children:(0,c.t)("Enable query cost estimation")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("For Bigquery, Presto and Postgres, shows a button to compute cost before running a query.")})]})}),(0,o.Y)(ie,{css:K,children:(0,o.FD)("div",{className:"input-container",children:[(0,o.Y)(H.A,{id:"allows_virtual_table_explore",name:"allows_virtual_table_explore",indeterminate:!1,checked:!1!==(null==y?void 0:y.allows_virtual_table_explore),onChange:l,children:(0,c.t)("Allow this database to be explored")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("When enabled, users are able to visualize SQL Lab results in Explore.")})]})}),(0,o.Y)(ie,{css:K,children:(0,o.FD)("div",{className:"input-container",children:[(0,o.Y)(H.A,{id:"disable_data_preview",name:"disable_data_preview",indeterminate:!1,checked:!(null==y||!y.disable_data_preview),onChange:l,children:(0,c.t)("Disable SQL Lab data preview queries")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("Disable data preview when fetching table metadata in SQL Lab.  Useful to avoid browser performance issues when using  databases with very wide tables.")})]})}),(0,o.Y)(ie,{children:(0,o.FD)("div",{className:"input-container",children:[(0,o.Y)(H.A,{id:"expand_rows",name:"expand_rows",indeterminate:!1,checked:!(null==y||null==(p=y.schema_options)||!p.expand_rows),onChange:l,children:(0,c.t)("Enable row expansion in schemas")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("For Trino, describe full schemas of nested ROW types, expanding them with dotted paths")})]})})]})]})})},{key:"performance",label:(0,o.Y)(q.s,{title:(0,c.t)("Performance"),subtitle:(0,c.t)("Adjust performance settings of this database."),testId:"performance-label-test"}),children:(0,o.FD)(o.FK,{children:[(0,o.FD)(ie,{className:"mb-8",children:[(0,o.Y)("div",{className:"control-label",children:(0,c.t)("Chart cache timeout")}),(0,o.Y)("div",{className:"input-container",children:(0,o.Y)(R.A,{type:"number",name:"cache_timeout",value:(null==e?void 0:e.cache_timeout)||"",placeholder:(0,c.t)("Enter duration in seconds"),onChange:a})}),(0,o.Y)("div",{className:"helper",children:(0,c.t)("Duration (in seconds) of the caching timeout for charts of this database. A timeout of 0 indicates that the cache never expires, and -1 bypasses the cache. Note this defaults to the global timeout if undefined.")})]}),(0,o.FD)(ie,{children:[(0,o.Y)("div",{className:"control-label",children:(0,c.t)("Schema cache timeout")}),(0,o.Y)("div",{className:"input-container",children:(0,o.Y)(R.A,{type:"number",name:"schema_cache_timeout",value:(null==y||null==(m=y.metadata_cache_timeout)?void 0:m.schema_cache_timeout)||"",placeholder:(0,c.t)("Enter duration in seconds"),onChange:l})}),(0,o.Y)("div",{className:"helper",children:(0,c.t)("Duration (in seconds) of the metadata caching timeout for schemas of this database. If left unset, the cache never expires.")})]}),(0,o.FD)(ie,{children:[(0,o.Y)("div",{className:"control-label",children:(0,c.t)("Table cache timeout")}),(0,o.Y)("div",{className:"input-container",children:(0,o.Y)(R.A,{type:"number",name:"table_cache_timeout",value:(null==y||null==(g=y.metadata_cache_timeout)?void 0:g.table_cache_timeout)||"",placeholder:(0,c.t)("Enter duration in seconds"),onChange:l})}),(0,o.Y)("div",{className:"helper",children:(0,c.t)("Duration (in seconds) of the metadata caching timeout for tables of this database. If left unset, the cache never expires. ")})]}),(0,o.Y)(ie,{css:{no_margin_bottom:K},children:(0,o.FD)("div",{className:"input-container",children:[(0,o.Y)(H.A,{id:"allow_run_async",name:"allow_run_async",indeterminate:!1,checked:N,onChange:a,children:(0,c.t)("Asynchronous query execution")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("Operate the database in asynchronous mode, meaning that the queries are executed on remote workers as opposed to on the web server itself. This assumes that you have a Celery worker setup as well as a results backend. Refer to the installation docs for more information.")}),$&&(0,o.Y)(D.I,{iconStyle:{color:A.colorError},tooltip:(0,c.t)("This option has been disabled by the administrator.")})]})}),(0,o.Y)(ie,{css:{no_margin_bottom:K},children:(0,o.FD)("div",{className:"input-container",children:[(0,o.Y)(H.A,{id:"cancel_query_on_windows_unload",name:"cancel_query_on_windows_unload",indeterminate:!1,checked:!(null==y||!y.cancel_query_on_windows_unload),onChange:l,children:(0,c.t)("Cancel query on window unload event")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("Terminate running queries when browser window closed or navigated to another page. Available for Presto, Hive, MySQL, Postgres and Snowflake databases.")})]})})]})},{key:"security",label:(0,o.Y)(q.s,{title:(0,c.t)("Security"),testId:"security-label-test",subtitle:(0,c.t)("Add extra connection information.")}),children:(0,o.FD)(o.FK,{children:[(0,o.FD)(ie,{children:[(0,o.Y)("div",{className:"control-label",children:(0,c.t)("Secure extra")}),(0,o.Y)("div",{className:"input-container",children:(0,o.Y)(re,{name:"masked_encrypted_extra",value:(null==e?void 0:e.masked_encrypted_extra)||"",placeholder:(0,c.t)("Secure extra"),onChange:e=>n({json:e,name:"masked_encrypted_extra"}),width:"100%",height:"160px",annotations:x})}),(0,o.Y)("div",{className:"helper",children:(0,o.Y)("div",{children:(0,c.t)("JSON string containing additional connection configuration. This is used to provide connection information for systems like Hive, Presto and BigQuery which do not conform to the username:password syntax normally used by SQLAlchemy.")})})]}),(0,o.FD)(ie,{children:[(0,o.Y)("div",{className:"control-label",children:(0,c.t)("Root certificate")}),(0,o.Y)("div",{className:"input-container",children:(0,o.Y)(R.A.TextArea,{name:"server_cert",value:(null==e?void 0:e.server_cert)||"",placeholder:(0,c.t)("Enter CA_BUNDLE"),onChange:t})}),(0,o.Y)("div",{className:"helper",children:(0,c.t)("Optional CA_BUNDLE contents to validate HTTPS requests. Only available on certain database engines.")})]}),(0,o.Y)(ie,{css:_?{}:K,children:(0,o.FD)("div",{className:"input-container",children:[(0,o.Y)(H.A,{id:"impersonate_user",name:"impersonate_user",indeterminate:!1,checked:!(null==e||!e.impersonate_user),onChange:a,children:(0,c.t)("Impersonate logged in user (Presto, Trino, Drill, Hive, and Google Sheets)")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("If Presto or Trino, all the queries in SQL Lab are going to be executed as the currently logged on user who must have permission to run them. If Hive and hive.server2.enable.doAs is enabled, will run the queries as service account, but impersonate the currently logged on user via hive.server2.proxy.user property.")})]})}),_&&(0,o.Y)(ie,{css:null!=e&&e.allow_file_upload?{}:K,children:(0,o.Y)("div",{className:"input-container",children:(0,o.Y)(H.A,{id:"allow_file_upload",name:"allow_file_upload",indeterminate:!1,checked:!(null==e||!e.allow_file_upload),onChange:a,children:(0,c.t)("Allow file uploads to database")})})}),_&&!(null==e||!e.allow_file_upload)&&(0,o.FD)(ie,{css:K,children:[(0,o.Y)("div",{className:"control-label",children:(0,c.t)("Schemas allowed for File upload")}),(0,o.Y)("div",{className:"input-container",children:(0,o.Y)(R.A,{type:"text",name:"schemas_allowed_for_file_upload",value:((null==y?void 0:y.schemas_allowed_for_file_upload)||[]).join(","),placeholder:"schema1,schema2",onChange:l})}),(0,o.Y)("div",{className:"helper",children:(0,c.t)("A comma-separated list of schemas that files are allowed to upload to.")})]})]})},...r&&F&&E?[{key:null==r?void 0:r.title,collapsible:null!=r.enabled&&r.enabled()?"icon":"disabled",label:(0,o.Y)(q.s,{title:(0,o.FD)(o.FK,{children:[k&&(0,o.Y)(k,{}),null==r?void 0:r.title]}),subtitle:(0,o.Y)(E,{})},null==r?void 0:r.title),children:(0,o.Y)(ie,{css:K,children:(0,o.Y)(F,{db:e,onEdit:r.onEdit})})}]:[],{key:"other",label:(0,o.Y)(q.s,{title:(0,c.t)("Other"),subtitle:(0,c.t)("Additional settings."),testId:"other-label-test"}),children:(0,o.FD)(o.FK,{children:[(0,o.FD)(ie,{children:[(0,o.Y)("div",{className:"control-label",children:(0,c.t)("Metadata Parameters")}),(0,o.Y)("div",{className:"input-container",children:(0,o.Y)(re,{name:"metadata_params",placeholder:(0,c.t)("Metadata Parameters"),onChange:e=>i({json:e,name:"metadata_params"}),width:"100%",height:"160px",value:Object.keys((null==y?void 0:y.metadata_params)||{}).length?"string"==typeof(null==y?void 0:y.metadata_params)?null==y?void 0:y.metadata_params:JSON.stringify(null==y?void 0:y.metadata_params):"",annotations:S})}),(0,o.Y)("div",{className:"helper",children:(0,o.Y)("div",{children:(0,c.t)("The metadata_params object gets unpacked into the sqlalchemy.MetaData call.")})})]}),(0,o.FD)(ie,{children:[(0,o.Y)("div",{className:"control-label",children:(0,c.t)("Engine Parameters")}),(0,o.Y)("div",{className:"input-container",children:(0,o.Y)(re,{name:"engine_params",placeholder:(0,c.t)("Engine Parameters"),onChange:e=>i({json:e,name:"engine_params"}),width:"100%",height:"160px",value:Object.keys((null==y?void 0:y.engine_params)||{}).length?null==y?void 0:y.engine_params:"",annotations:w})}),(0,o.Y)("div",{className:"helper",children:(0,o.Y)("div",{children:(0,c.t)("The engine_params object gets unpacked into the sqlalchemy.create_engine call.")})})]}),(0,o.FD)(ie,{children:[(0,o.Y)("div",{className:"control-label",children:(0,c.t)("Version")}),(0,o.Y)("div",{className:"input-container",children:(0,o.Y)(R.A,{type:"text",name:"version",placeholder:(0,c.t)("Version number"),onChange:l,value:(null==y?void 0:y.version)||""})}),(0,o.Y)("div",{className:"helper",children:(0,c.t)("Specify the database version. This is used with Presto for query cost estimation, and Dremio for syntax changes, among others.")})]}),(0,o.Y)(ie,{css:K,children:(0,o.FD)("div",{className:"input-container",children:[(0,o.Y)(H.A,{id:"disable_drill_to_detail",name:"disable_drill_to_detail",indeterminate:!1,checked:!(null==y||!y.disable_drill_to_detail),onChange:l,children:(0,c.t)("Disable drill to detail")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("Disables the drill to detail feature for this database.")})]})}),f&&(0,o.Y)(ie,{css:K,children:(0,o.FD)("div",{className:"input-container",children:[(0,o.Y)(H.A,{id:"allow_multi_catalog",name:"allow_multi_catalog",indeterminate:!1,checked:!(null==y||!y.allow_multi_catalog),onChange:l,children:(0,c.t)("Allow changing catalogs")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("Give access to multiple catalogs in a single database connection.")})]})})]})}]})};var xe=t(7840);const Ye=({db:e,onInputChange:a,testConnection:t,conf:n,testInProgress:l=!1,children:i})=>{var r,s;const d=(null==xe.A||null==(r=xe.A.DB_MODAL_SQLALCHEMY_FORM)?void 0:r.SQLALCHEMY_DOCS_URL)||"https://docs.sqlalchemy.org/en/13/core/engines.html",h=(null==xe.A||null==(s=xe.A.DB_MODAL_SQLALCHEMY_FORM)?void 0:s.SQLALCHEMY_DISPLAY_TEXT)||"SQLAlchemy docs";return(0,o.FD)(o.FK,{children:[(0,o.FD)(ie,{children:[(0,o.FD)("div",{className:"control-label",children:[(0,c.t)("Display Name"),(0,o.Y)("span",{className:"required",children:"*"})]}),(0,o.Y)("div",{className:"input-container",children:(0,o.Y)(R.A,{name:"database_name",value:(null==e?void 0:e.database_name)||"",placeholder:(0,c.t)("Name your database"),onChange:a})}),(0,o.Y)("div",{className:"helper",children:(0,c.t)("Pick a name to help you identify this database.")})]}),(0,o.FD)(ie,{children:[(0,o.FD)("div",{className:"control-label",children:[(0,c.t)("SQLAlchemy URI"),(0,o.Y)("span",{className:"required",children:"*"})]}),(0,o.Y)("div",{className:"input-container",children:(0,o.Y)(R.A,{name:"sqlalchemy_uri",value:(null==e?void 0:e.sqlalchemy_uri)||"",autoComplete:"off",placeholder:(null==e?void 0:e.sqlalchemy_uri_placeholder)||(0,c.t)("dialect+driver://username:password@host:port/database"),onChange:a})}),(0,o.FD)("div",{className:"helper",children:[(0,c.t)("Refer to the")," ",(0,o.Y)("a",{href:d||(null==n?void 0:n.SQLALCHEMY_DOCS_URL)||"",target:"_blank",rel:"noopener noreferrer",children:h||(null==n?void 0:n.SQLALCHEMY_DISPLAY_TEXT)||""})," ",(0,c.t)("for more information on how to structure your URI.")]})]}),i,(0,o.Y)(F.$,{onClick:t,loading:l,cta:!0,buttonStyle:"link",css:e=>(e=>_.AH`
  width: 100%;
  border: 1px solid ${e.colorPrimaryText};
  color: ${e.colorPrimaryText};
  &:hover,
  &:focus {
    border: 1px solid ${e.colorPrimary};
    color: ${e.colorPrimary};
  }
`)(e),children:(0,c.t)("Test connection")})]})};var Se=t(65729),Ce=t(15039),we=t(82384);const Ae={account:{label:"Account",helpText:(0,c.t)("Copy the identifier of the account you are trying to connect to."),placeholder:(0,c.t)("e.g. xy12345.us-east-2.aws")},warehouse:{label:"Warehouse",placeholder:(0,c.t)("e.g. compute_wh"),className:"form-group-w-50"},role:{label:"Role",placeholder:(0,c.t)("e.g. AccountAdmin"),className:"form-group-w-50"}},Fe=({required:e,changeMethods:a,getValidation:t,validationErrors:n,db:l,field:i})=>{var r,s;return(0,o.Y)(A.M,{id:i,name:i,required:e,value:null==l||null==(r=l.parameters)?void 0:r[i],validationMethods:{onBlur:t},errorMessage:null==n?void 0:n[i],placeholder:Ae[i].placeholder,helpText:null==(s=Ae[i])?void 0:s.helpText,label:Ae[i].label||i,onChange:a.onParametersChange,className:Ae[i].className||i})};var ke;!function(e){e[e.JsonUpload=0]="JsonUpload",e[e.CopyPaste=1]="CopyPaste"}(ke||(ke={}));const De={gsheets:"service_account_info",bigquery:"credentials_info"},Ee=({changeMethods:e,isEditMode:a,db:t,editNewDb:n})=>{var l;const[i,r]=(0,h.useState)([]),[s,d]=(0,h.useState)(ke.JsonUpload.valueOf()),{addDangerToast:u}=(0,T.Yf)(),p=!a,m=(null==t?void 0:t.engine)&&De[t.engine],v=null==t||null==(l=t.parameters)?void 0:l[m],f=v&&"object"==typeof v?JSON.stringify(v):v;return(0,h.useEffect)((()=>{e.onParametersChange({target:{name:m,value:""}})}),[]),(0,o.FD)(me,{children:[p&&(0,o.FD)(o.FK,{children:[(0,o.Y)(g.l,{children:(0,c.t)("How do you want to enter service account credentials?")}),(0,o.Y)(b.A,{defaultValue:s,css:_.AH`
              width: 100%;
            `,onChange:e=>d(e),options:[{value:ke.JsonUpload,label:(0,c.t)("Upload JSON file")},{value:ke.CopyPaste,label:(0,c.t)("Copy and Paste JSON credentials")}]})]}),s===ke.CopyPaste||a||n?(0,o.FD)("div",{className:"input-container",children:[(0,o.Y)(g.l,{children:(0,c.t)("Service Account")}),(0,o.Y)(R.A.TextArea,{className:"input-form",name:m,value:"boolean"==typeof f?String(f):f,onChange:e.onParametersChange,placeholder:(0,c.t)("Paste content of service credentials JSON file here")})]}):p&&(0,o.Y)("div",{className:"input-container",css:e=>Q(e),children:(0,o.Y)(E.A,{accept:".json",maxCount:1,fileList:i,beforeUpload:()=>!1,onRemove:()=>(r([]),e.onParametersChange({target:{name:m,value:""}}),!0),onChange:async a=>{var t;const n=null==(t=a.fileList)||null==(t=t[0])?void 0:t.originFileObj;if(n)try{const t=await(e=>new Promise(((a,t)=>{const n=new FileReader;n.readAsText(e),n.onload=()=>a(n.result),n.onerror=t})))(n);e.onParametersChange({target:{type:null,name:m,value:t,checked:!1}}),r(a.fileList)}catch(e){r([]),u((0,c.t)("Unable to read the file, please refresh and try again."))}else e.onParametersChange({target:{name:m,value:""}})},children:(0,o.Y)(F.$,{icon:(0,o.Y)(y.F.LinkOutlined,{iconSize:"m"}),children:(0,c.t)("Upload credentials")})})})]})},Ne=({clearValidationErrors:e,changeMethods:a,db:t,dbModel:n})=>{var l,i,s;const[d,u]=(0,h.useState)(!1),p=(0,I.G7)(I.TO.SshTunneling),m=(null==n||null==(l=n.engine_information)?void 0:l.disable_ssh_tunneling)||!1,g=p&&!m;return(0,h.useEffect)((()=>{var e;g&&void 0!==(null==t||null==(e=t.parameters)?void 0:e.ssh)&&u(t.parameters.ssh)}),[null==t||null==(i=t.parameters)?void 0:i.ssh,g]),(0,h.useEffect)((()=>{var e;g&&void 0===(null==t||null==(e=t.parameters)?void 0:e.ssh)&&!r()(null==t?void 0:t.ssh_tunnel)&&a.onParametersChange({target:{type:"toggle",name:"ssh",checked:!0,value:!0}})}),[a,null==t||null==(s=t.parameters)?void 0:s.ssh,null==t?void 0:t.ssh_tunnel,g]),g?(0,o.FD)("div",{css:e=>Q(e),children:[(0,o.Y)(Ce.A,{checked:d,onChange:t=>{u(t),a.onParametersChange({target:{type:"toggle",name:"ssh",checked:!0,value:t}}),e()}}),(0,o.Y)("span",{css:W,children:(0,c.t)("SSH Tunnel")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("SSH Tunnel configuration parameters"),placement:"right"})]}):null};var $e;const Te=["host","port","database","default_catalog","default_schema","username","password","access_token","http_path","http_path_field","database_name","project_id","catalog","credentials_info","service_account_info","query","encryption","account","warehouse","role","ssh","oauth2_client_info"],Me={host:({required:e,changeMethods:a,getValidation:t,validationErrors:n,db:l,isValidating:i})=>{var r;return(0,o.Y)(A.M,{isValidating:i,id:"host",name:"host",value:null==l||null==(r=l.parameters)?void 0:r.host,required:e,hasTooltip:!0,tooltipText:(0,c.t)("This can be either an IP address (e.g. 127.0.0.1) or a domain name (e.g. mydatabase.com)."),validationMethods:{onBlur:t},errorMessage:null==n?void 0:n.host,placeholder:(0,c.t)("e.g. 127.0.0.1"),className:"form-group-w-50",label:(0,c.t)("Host"),onChange:a.onParametersChange})},http_path:({required:e,changeMethods:a,getValidation:t,validationErrors:n,db:l,isValidating:i})=>{var r;const s=JSON.parse((null==l?void 0:l.extra)||"{}");return(0,o.Y)(A.M,{isValidating:i,id:"http_path",name:"http_path",required:e,value:null==(r=s.engine_params)||null==(r=r.connect_args)?void 0:r.http_path,validationMethods:{onBlur:t},errorMessage:null==n?void 0:n.http_path,placeholder:(0,c.t)("e.g. sql/protocolv1/o/12345"),label:"HTTP Path",onChange:a.onExtraInputChange,helpText:(0,c.t)("Copy the name of the HTTP Path of your cluster.")})},http_path_field:({required:e,changeMethods:a,getValidation:t,validationErrors:n,db:l,isValidating:i})=>{var r;return(0,o.Y)(A.M,{id:"http_path_field",name:"http_path_field",required:e,isValidating:i,value:null==l||null==(r=l.parameters)?void 0:r.http_path_field,validationMethods:{onBlur:t},errorMessage:null==n?void 0:n.http_path,placeholder:(0,c.t)("e.g. sql/protocolv1/o/12345"),label:"HTTP Path",onChange:a.onParametersChange,helpText:(0,c.t)("Copy the name of the HTTP Path of your cluster.")})},port:({required:e,changeMethods:a,getValidation:t,validationErrors:n,db:l,isValidating:i})=>{var r;return(0,o.Y)(o.FK,{children:(0,o.Y)(A.M,{id:"port",name:"port",type:"number",isValidating:i,required:e,value:null==l||null==(r=l.parameters)?void 0:r.port,validationMethods:{onBlur:t},errorMessage:null==n?void 0:n.port,placeholder:(0,c.t)("e.g. 5432"),className:"form-group-w-50",label:(0,c.t)("Port"),onChange:a.onParametersChange})})},database:({required:e,changeMethods:a,getValidation:t,validationErrors:n,placeholder:l,db:i,isValidating:r})=>{var s;return(0,o.Y)(A.M,{isValidating:r,id:"database",name:"database",required:e,value:null==i||null==(s=i.parameters)?void 0:s.database,validationMethods:{onBlur:t},errorMessage:null==n?void 0:n.database,placeholder:null!=l?l:(0,c.t)("e.g. world_population"),label:(0,c.t)("Database name"),onChange:a.onParametersChange,helpText:(0,c.t)("Copy the name of the database you are trying to connect to.")})},default_catalog:({required:e,changeMethods:a,getValidation:t,validationErrors:n,db:l,isValidating:i})=>{var r;return(0,o.Y)(A.M,{isValidating:i,id:"default_catalog",name:"default_catalog",required:e,value:null==l||null==(r=l.parameters)?void 0:r.default_catalog,validationMethods:{onBlur:t},errorMessage:null==n?void 0:n.default_catalog,placeholder:(0,c.t)("e.g. hive_metastore"),label:(0,c.t)("Default Catalog"),onChange:a.onParametersChange,helpText:(0,c.t)("The default catalog that should be used for the connection.")})},default_schema:({required:e,changeMethods:a,getValidation:t,validationErrors:n,db:l,isValidating:i})=>{var r;return(0,o.Y)(A.M,{id:"default_schema",name:"default_schema",required:e,isValidating:i,value:null==l||null==(r=l.parameters)?void 0:r.default_schema,validationMethods:{onBlur:t},errorMessage:null==n?void 0:n.default_schema,placeholder:(0,c.t)("e.g. default"),label:(0,c.t)("Default Schema"),onChange:a.onParametersChange,helpText:(0,c.t)("The default schema that should be used for the connection.")})},username:({required:e,changeMethods:a,getValidation:t,validationErrors:n,db:l,isValidating:i})=>{var r;return(0,o.Y)(A.M,{id:"username",name:"username",required:e,isValidating:i,value:null==l||null==(r=l.parameters)?void 0:r.username,validationMethods:{onBlur:t},errorMessage:null==n?void 0:n.username,placeholder:(0,c.t)("e.g. Analytics"),label:(0,c.t)("Username"),onChange:a.onParametersChange})},password:({required:e,changeMethods:a,getValidation:t,validationErrors:n,db:l,isEditMode:i,isValidating:r})=>{var s;return(0,o.Y)(A.M,{id:"password",name:"password",required:e,isValidating:r,visibilityToggle:!i,value:null==l||null==(s=l.parameters)?void 0:s.password,validationMethods:{onBlur:t},errorMessage:null==n?void 0:n.password,placeholder:(0,c.t)("e.g. ********"),label:(0,c.t)("Password"),onChange:a.onParametersChange})},oauth2_client_info:({changeMethods:e,db:a,default_value:t})=>{var n,l,i,r,s;const d=JSON.parse((null==a?void 0:a.masked_encrypted_extra)||"{}"),[c,u]=(0,h.useState)({id:(null==(n=d.oauth2_client_info)?void 0:n.id)||"",secret:(null==(l=d.oauth2_client_info)?void 0:l.secret)||"",authorization_request_uri:(null==(i=d.oauth2_client_info)?void 0:i.authorization_request_uri)||(null==t?void 0:t.authorization_request_uri)||"",token_request_uri:(null==(r=d.oauth2_client_info)?void 0:r.token_request_uri)||(null==t?void 0:t.token_request_uri)||"",scope:(null==(s=d.oauth2_client_info)?void 0:s.scope)||(null==t?void 0:t.scope)||""}),p=a=>t=>{const n={...c,[a]:t.target.value};u(n);const l={target:{type:"object",name:"oauth2_client_info",value:n}};e.onParametersChange(l)};return(0,o.Y)(O.S,{items:[{key:"oauth2-client-information",label:"OAuth2 client information",children:(0,o.FD)(o.FK,{children:[(0,o.Y)(we.e,{label:"Client ID",children:(0,o.Y)(R.A,{value:c.id,onChange:p("id")})}),(0,o.Y)(we.e,{label:"Client Secret",children:(0,o.Y)(R.A,{type:"password",value:c.secret,onChange:p("secret")})}),(0,o.Y)(we.e,{label:"Authorization Request URI",children:(0,o.Y)(R.A,{placeholder:"https://",value:c.authorization_request_uri,onChange:p("authorization_request_uri")})}),(0,o.Y)(we.e,{label:"Token Request URI",children:(0,o.Y)(R.A,{placeholder:"https://",value:c.token_request_uri,onChange:p("token_request_uri")})}),(0,o.Y)(we.e,{label:"Scope",children:(0,o.Y)(R.A,{value:c.scope,onChange:p("scope")})})]})}]})},access_token:({required:e,changeMethods:a,getValidation:t,validationErrors:n,db:l,isEditMode:i,default_value:r,description:s})=>{var d;return(0,o.Y)(A.M,{id:"access_token",name:"access_token",required:e,visibilityToggle:!i,value:null==l||null==(d=l.parameters)?void 0:d.access_token,validationMethods:{onBlur:t},errorMessage:null==n?void 0:n.access_token,placeholder:(0,c.t)("Paste your access token here"),get_url:"string"==typeof r&&r.includes("https://")?r:null,description:s,label:(0,c.t)("Access token"),onChange:a.onParametersChange})},database_name:({changeMethods:e,getValidation:a,validationErrors:t,db:n,isValidating:l})=>(0,o.Y)(o.FK,{children:(0,o.Y)(A.M,{id:"database_name",name:"database_name",required:!0,isValidating:l,value:null==n?void 0:n.database_name,validationMethods:{onBlur:a},errorMessage:null==t?void 0:t.database_name,placeholder:"",label:(0,c.t)("Display Name"),onChange:e.onChange,helpText:(0,c.t)("Pick a nickname for how the database will display in Superset.")})}),query:({required:e,changeMethods:a,getValidation:t,validationErrors:n,db:l,isValidating:i})=>(0,o.Y)(A.M,{id:"query_input",name:"query_input",required:e,isValidating:i,value:(null==l?void 0:l.query_input)||"",validationMethods:{onBlur:t},errorMessage:null==n?void 0:n.query,placeholder:(0,c.t)("e.g. param1=value1&param2=value2"),label:(0,c.t)("Additional Parameters"),onChange:a.onQueryChange,helpText:(0,c.t)("Add additional custom parameters")}),encryption:({isEditMode:e,changeMethods:a,db:t,sslForced:n})=>{var l;return(0,o.FD)("div",{css:e=>Q(e),children:[(0,o.Y)(Ce.A,{disabled:n&&!e,checked:(null==t||null==(l=t.parameters)?void 0:l.encryption)||n,onChange:e=>{a.onParametersChange({target:{type:"toggle",name:"encryption",checked:!0,value:e}})}}),(0,o.Y)("span",{css:W,children:"SSL"}),(0,o.Y)(D.I,{tooltip:(0,c.t)('SSL Mode "require" will be used.'),placement:"right"})]})},credentials_info:Ee,service_account_info:Ee,catalog:({required:e,changeMethods:a,getValidation:t,validationErrors:n,db:l})=>{const i=(null==l?void 0:l.catalog)||[],r=n||{};return(0,o.FD)(_e,{children:[(0,o.Y)(f.o.Title,{level:4,className:"gsheet-title",children:(0,c.t)("Connect Google Sheets as tables to this database")}),(0,o.FD)("div",{children:[null==i?void 0:i.map(((n,l)=>{var s,d;return(0,o.FD)(o.FK,{children:[(0,o.Y)(g.l,{className:"catalog-label",children:(0,c.t)("Google Sheet Name and URL")}),(0,o.FD)("div",{className:"catalog-name",children:[(0,o.Y)(A.M,{className:"catalog-name-input",required:e,validationMethods:{onBlur:t},errorMessage:null==(s=r[l])?void 0:s.name,placeholder:(0,c.t)("Enter a name for this sheet"),onChange:e=>{a.onParametersChange({target:{type:`catalog-${l}`,name:"name",value:e.target.value}})},value:n.name}),(null==i?void 0:i.length)>1&&(0,o.Y)(y.F.CloseOutlined,{css:e=>_.AH`
                    align-self: center;
                    background: ${e.colorFillSecondary};
                    margin: 5px 5px 8px 5px;

                    &.anticon > * {
                      line-height: 0;
                    }
                  `,iconSize:"m",onClick:()=>a.onRemoveTableCatalog(l)})]}),(0,o.Y)(A.M,{className:"catalog-name-url",required:e,validationMethods:{onBlur:t},errorMessage:null==(d=r[l])?void 0:d.url,placeholder:(0,c.t)("Paste the shareable Google Sheet URL here"),onChange:e=>a.onParametersChange({target:{type:`catalog-${l}`,name:"value",value:e.target.value}}),value:n.value})]})})),(0,o.FD)(be,{className:"catalog-add-btn",onClick:()=>{a.onAddTableCatalog()},children:["+ ",(0,c.t)("Add sheet")]})]}),(0,o.Y)("div",{className:"helper",children:(0,o.Y)("div",{children:(0,c.t)("In order to connect to non-public sheets you need to either provide a service account or configure an OAuth2 client.")})})]})},warehouse:Fe,role:Fe,account:Fe,ssh:null!=($e=(0,s.a)().get("ssh_tunnel.form.switch"))?$e:Ne,project_id:({changeMethods:e,getValidation:a,validationErrors:t,db:n,isValidating:l})=>{var i;return(0,o.Y)(o.FK,{children:(0,o.Y)(A.M,{id:"project_id",name:"project_id",required:!0,isValidating:l,value:null==n||null==(i=n.parameters)?void 0:i.project_id,validationMethods:{onBlur:a},errorMessage:null==t?void 0:t.project_id,placeholder:"your-project-1234-a1",label:(0,c.t)("Project Id"),onChange:e.onParametersChange,helpText:(0,c.t)("Enter the unique project id for your database.")})})}},ze=({dbModel:e,db:a,editNewDb:t,getPlaceholder:n,getValidation:l,isEditMode:i=!1,onAddTableCatalog:r,onChange:s,onExtraInputChange:d,onEncryptedExtraInputChange:c,onParametersChange:h,onParametersUploadFileChange:u,onQueryChange:p,onRemoveTableCatalog:m,sslForced:g,validationErrors:b,clearValidationErrors:v,isValidating:_})=>{const f=null==e?void 0:e.parameters;return(0,o.Y)(Se.l,{children:(0,o.Y)("div",{css:e=>[X,le(e)],children:f&&Te.filter((e=>Object.keys(f.properties).includes(e)||"database_name"===e)).map((e=>{var o,y,x;return Me[e]({required:null==(o=f.required)?void 0:o.includes(e),changeMethods:{onParametersChange:h,onChange:s,onQueryChange:p,onParametersUploadFileChange:u,onAddTableCatalog:r,onRemoveTableCatalog:m,onExtraInputChange:d,onEncryptedExtraInputChange:c},validationErrors:b,getValidation:l,clearValidationErrors:v,db:a,key:e,field:e,default_value:null==(y=f.properties[e])?void 0:y.default,description:null==(x=f.properties[e])?void 0:x.description,isEditMode:i,sslForced:g,editNewDb:t,isValidating:_,placeholder:n?n(e):void 0})}))})})},Le=(0,M.xK)(),Pe=Le?Le.support:"https://superset.apache.org/docs/configuration/databases#installing-database-drivers",Ue={postgresql:"https://superset.apache.org",mssql:"https://superset.apache.org/docs/databases/sql-server",gsheets:"https://superset.apache.org/docs/databases/google-sheets"},Ie=({isLoading:e,isEditMode:a,useSqlAlchemyForm:t,hasConnectedDb:n,db:l,dbName:i,dbModel:r,editNewDb:s,fileList:d})=>{const h=d&&(null==d?void 0:d.length)>0,u=(0,o.FD)(B,{children:[(0,o.Y)(ue,{children:null==l?void 0:l.backend}),(0,o.Y)(pe,{children:i})]}),p=(0,o.FD)(B,{children:[(0,o.Y)("p",{className:"helper-top",children:(0,c.t)("STEP %(stepCurr)s OF %(stepLast)s",{stepCurr:2,stepLast:2})}),(0,o.Y)(f.o.Title,{level:4,children:(0,c.t)("Enter Primary Credentials")}),(0,o.FD)("p",{className:"helper-bottom",children:[(0,c.t)("Need help? Learn how to connect your database")," ",(0,o.Y)("a",{href:(null==Le?void 0:Le.default)||Pe,target:"_blank",rel:"noopener noreferrer",children:(0,c.t)("here")}),"."]})]}),m=(0,o.Y)(ve,{children:(0,o.FD)(B,{children:[(0,o.Y)("p",{className:"helper-top",children:(0,c.t)("STEP %(stepCurr)s OF %(stepLast)s",{stepCurr:3,stepLast:3})}),(0,o.Y)(f.o.Title,{level:4,className:"step-3-text",children:(0,c.t)("Database connected")}),(0,o.Y)("p",{className:"subheader-text",children:(0,c.t)("Create a dataset to begin visualizing your data as a chart or go to\n          SQL Lab to query your data.")})]})}),g=(0,o.Y)(ve,{children:(0,o.FD)(B,{children:[(0,o.Y)("p",{className:"helper-top",children:(0,c.t)("STEP %(stepCurr)s OF %(stepLast)s",{stepCurr:2,stepLast:3})}),(0,o.Y)(f.o.Title,{level:4,children:(0,c.t)("Enter the required %(dbModelName)s credentials",{dbModelName:r.name})}),(0,o.FD)("p",{className:"helper-bottom",children:[(0,c.t)("Need help? Learn more about")," ",(0,o.FD)("a",{href:(b=null==l?void 0:l.engine,b?Le?Le[b]||Le.default:Ue[b]?Ue[b]:`https://superset.apache.org/docs/databases/${b}`:null),target:"_blank",rel:"noopener noreferrer",children:[(0,c.t)("connecting to %(dbModelName)s",{dbModelName:r.name}),"."]})]})]})});var b;const v=(0,o.Y)(ve,{children:(0,o.Y)(B,{children:(0,o.FD)("div",{className:"select-db",children:[(0,o.Y)("p",{className:"helper-top",children:(0,c.t)("STEP %(stepCurr)s OF %(stepLast)s",{stepCurr:1,stepLast:3})}),(0,o.Y)(f.o.Title,{level:4,children:(0,c.t)("Select a database to connect")})]})})}),_=(0,o.Y)(ve,{children:(0,o.FD)(B,{children:[(0,o.Y)("p",{className:"helper-top",children:(0,c.t)("STEP %(stepCurr)s OF %(stepLast)s",{stepCurr:2,stepLast:2})}),(0,o.Y)(f.o.Title,{level:4,children:(0,c.t)("Enter the required %(dbModelName)s credentials",{dbModelName:r.name})}),(0,o.Y)("p",{className:"helper-bottom",children:h?d[0].name:""})]})});return h?_:e?(0,o.Y)(o.FK,{}):a?u:t?p:n&&!s?m:l||s?g:v};var Oe=t(47152),qe=t(16370),He=t(22750);const Re=d.I4.div`
  padding-top: ${({theme:e})=>2*e.sizeUnit}px;
  label {
    color: ${({theme:e})=>e.colorText};
    margin-bottom: ${({theme:e})=>2*e.sizeUnit}px;
  }
`,Ve=(0,d.I4)(Oe.A)`
  padding-bottom: ${({theme:e})=>2*e.sizeUnit}px;
`,je=(0,d.I4)(Se.l.Item)`
  margin-bottom: 0 !important;
`,Ke=(0,d.I4)(R.A.Password)`
  margin: ${({theme:e})=>`${e.sizeUnit}px 0 ${2*e.sizeUnit}px`};
`,Be=({db:e,onSSHTunnelParametersChange:a,setSSHTunnelLoginMethod:t})=>{var n,l,i,r,s,d;const[u,p]=(0,h.useState)(ta.Password);return(0,o.FD)(Se.l,{children:[(0,o.FD)(Ve,{gutter:16,children:[(0,o.Y)(qe.A,{xs:24,md:12,children:(0,o.FD)(Re,{children:[(0,o.Y)(g.l,{htmlFor:"server_address",required:!0,children:(0,c.t)("SSH Host")}),(0,o.Y)(R.A,{name:"server_address",type:"text",placeholder:(0,c.t)("e.g. 127.0.0.1"),value:(null==e||null==(n=e.ssh_tunnel)?void 0:n.server_address)||"",onChange:a})]})}),(0,o.Y)(qe.A,{xs:24,md:12,children:(0,o.FD)(Re,{children:[(0,o.Y)(g.l,{htmlFor:"server_port",required:!0,children:(0,c.t)("SSH Port")}),(0,o.Y)(R.A,{name:"server_port",placeholder:(0,c.t)("22"),type:"number",value:null==e||null==(l=e.ssh_tunnel)?void 0:l.server_port,onChange:a})]})})]}),(0,o.Y)(Ve,{gutter:16,children:(0,o.Y)(qe.A,{xs:24,children:(0,o.FD)(Re,{children:[(0,o.Y)(g.l,{htmlFor:"username",required:!0,children:(0,c.t)("Username")}),(0,o.Y)(R.A,{name:"username",type:"text",placeholder:(0,c.t)("e.g. Analytics"),value:(null==e||null==(i=e.ssh_tunnel)?void 0:i.username)||"",onChange:a})]})})}),(0,o.Y)(Ve,{gutter:16,children:(0,o.Y)(qe.A,{xs:24,children:(0,o.FD)(Re,{children:[(0,o.Y)(g.l,{htmlFor:"use_password",required:!0,children:(0,c.t)("Login with")}),(0,o.Y)(je,{name:"use_password",initialValue:u,children:(0,o.FD)(He.s.Group,{onChange:({target:{value:e}})=>{p(e),t(e)},children:[(0,o.Y)(He.s,{value:ta.Password,children:(0,c.t)("Password")}),(0,o.Y)(He.s,{value:ta.PrivateKey,children:(0,c.t)("Private Key & Password")})]})})]})})}),u===ta.Password&&(0,o.Y)(Ve,{gutter:16,children:(0,o.Y)(qe.A,{xs:24,children:(0,o.FD)(Re,{children:[(0,o.Y)(g.l,{htmlFor:"password",required:!0,children:(0,c.t)("SSH Password")}),(0,o.Y)(Ke,{name:"password",placeholder:(0,c.t)("e.g. ********"),value:(null==e||null==(r=e.ssh_tunnel)?void 0:r.password)||"",onChange:a,iconRender:e=>e?(0,o.Y)(Y.m,{title:"Hide password.",children:(0,o.Y)(y.F.EyeInvisibleOutlined,{})}):(0,o.Y)(Y.m,{title:"Show password.",children:(0,o.Y)(y.F.EyeOutlined,{})}),role:"textbox"})]})})}),u===ta.PrivateKey&&(0,o.FD)(o.FK,{children:[(0,o.Y)(Ve,{gutter:16,children:(0,o.Y)(qe.A,{xs:24,children:(0,o.FD)(Re,{children:[(0,o.Y)(g.l,{htmlFor:"private_key",required:!0,children:(0,c.t)("Private Key")}),(0,o.Y)(R.A.TextArea,{name:"private_key",placeholder:(0,c.t)("Paste Private Key here"),value:(null==e||null==(s=e.ssh_tunnel)?void 0:s.private_key)||"",onChange:a,rows:4})]})})}),(0,o.Y)(Ve,{gutter:16,children:(0,o.Y)(qe.A,{xs:24,children:(0,o.FD)(Re,{children:[(0,o.Y)(g.l,{htmlFor:"private_key_password",required:!0,children:(0,c.t)("Private Key Password")}),(0,o.Y)(Ke,{name:"private_key_password",placeholder:(0,c.t)("e.g. ********"),value:(null==e||null==(d=e.ssh_tunnel)?void 0:d.private_key_password)||"",onChange:a,iconRender:e=>e?(0,o.Y)(Y.m,{title:"Hide password.",children:(0,o.Y)(y.F.EyeInvisibleOutlined,{})}):(0,o.Y)(Y.m,{title:"Show password.",children:(0,o.Y)(y.F.EyeOutlined,{})}),role:"textbox"})]})})})]})]})},Je=(0,s.a)(),Ge=JSON.stringify({allows_virtual_table_explore:!0}),Qe="basic",We={[w.GSheet]:{message:"Why do I need to create a database?",description:"To begin using your Google Sheets, you need to create a database first. Databases are used as a way to identify your data so that it can be queried and visualized. This database will hold all of your individual Google Sheets you choose to connect here."}},Xe=(0,d.I4)(m.Ay)`
  .ant-tabs-content {
    width: 100%;
    overflow: inherit;

    & > .ant-tabs-tabpane {
      position: relative;
    }
  }
`,Ze=d.I4.div`
  ${({theme:e})=>`\n    margin: ${8*e.sizeUnit}px ${4*e.sizeUnit}px;\n  `};
`,ea=d.I4.div`
  ${({theme:e})=>`\n    padding: 0px ${4*e.sizeUnit}px;\n  `};
`;var aa,ta;!function(e){e[e.AddTableCatalogSheet=0]="AddTableCatalogSheet",e[e.ConfigMethodChange=1]="ConfigMethodChange",e[e.DbSelected=2]="DbSelected",e[e.EditorChange=3]="EditorChange",e[e.ExtraEditorChange=4]="ExtraEditorChange",e[e.ExtraInputChange=5]="ExtraInputChange",e[e.EncryptedExtraInputChange=6]="EncryptedExtraInputChange",e[e.Fetched=7]="Fetched",e[e.InputChange=8]="InputChange",e[e.ParametersChange=9]="ParametersChange",e[e.QueryChange=10]="QueryChange",e[e.RemoveTableCatalogSheet=11]="RemoveTableCatalogSheet",e[e.Reset=12]="Reset",e[e.TextChange=13]="TextChange",e[e.ParametersSSHTunnelChange=14]="ParametersSSHTunnelChange",e[e.SetSSHTunnelLoginMethod=15]="SetSSHTunnelLoginMethod",e[e.RemoveSSHTunnelConfig=16]="RemoveSSHTunnelConfig"}(aa||(aa={})),function(e){e[e.Password=0]="Password",e[e.PrivateKey=1]="PrivateKey"}(ta||(ta={}));const na=d.I4.div`
  display: flex;
  justify-content: center;
  padding: ${({theme:e})=>5*e.sizeUnit}px;
`;function la(e,a){var t,n,i;const r={...e||{}};let o,s,d={},c="";const h=JSON.parse(r.extra||"{}");switch(a.type){case aa.ExtraEditorChange:try{s=JSON.parse(a.payload.json||"{}")}catch(e){s=a.payload.json}return{...r,extra:JSON.stringify({...h,[a.payload.name]:s})};case aa.EncryptedExtraInputChange:return{...r,masked_encrypted_extra:JSON.stringify({...JSON.parse(r.masked_encrypted_extra||"{}"),[a.payload.name]:a.payload.value})};case aa.ExtraInputChange:return"schema_cache_timeout"===a.payload.name||"table_cache_timeout"===a.payload.name?{...r,extra:JSON.stringify({...h,metadata_cache_timeout:{...null==h?void 0:h.metadata_cache_timeout,[a.payload.name]:Number(a.payload.value)}})}:"schemas_allowed_for_file_upload"===a.payload.name?{...r,extra:JSON.stringify({...h,schemas_allowed_for_file_upload:(a.payload.value||"").split(",").filter((e=>""!==e))})}:"http_path"===a.payload.name?{...r,extra:JSON.stringify({...h,engine_params:{connect_args:{[a.payload.name]:null==(u=a.payload.value)?void 0:u.trim()}}})}:"expand_rows"===a.payload.name?{...r,extra:JSON.stringify({...h,schema_options:{...null==h?void 0:h.schema_options,[a.payload.name]:"checked"in a.payload?!!a.payload.checked:!!a.payload.value}})}:{...r,extra:JSON.stringify({...h,[a.payload.name]:"checkbox"===a.payload.type?a.payload.checked:a.payload.value})};var u;case aa.InputChange:return"checkbox"===a.payload.type?{...r,[a.payload.name]:a.payload.checked}:{...r,[a.payload.name]:a.payload.value};case aa.ParametersChange:if(null!=(t=a.payload.type)&&t.startsWith("catalog")&&void 0!==r.catalog){var p;const e=[...r.catalog],t=null==(p=a.payload.type)?void 0:p.split("-")[1],n=e[parseInt(t,10)]||{};return void 0!==a.payload.value&&(n[a.payload.name]=a.payload.value),e.splice(parseInt(t,10),1,n),o=e.reduce(((e,a)=>{const t={...e};return t[a.name]=a.value,t}),{}),{...r,catalog:e,parameters:{...r.parameters,catalog:o}}}return{...r,parameters:{...r.parameters,[a.payload.name]:a.payload.value}};case aa.ParametersSSHTunnelChange:return{...r,ssh_tunnel:{...r.ssh_tunnel,[a.payload.name]:a.payload.value}};case aa.SetSSHTunnelLoginMethod:{let e={};var m,g,b;return null!=r&&r.ssh_tunnel&&(e=l()(r.ssh_tunnel,["id","server_address","server_port","username"])),a.payload.login_method===ta.PrivateKey?{...r,ssh_tunnel:{private_key:null==r||null==(m=r.ssh_tunnel)?void 0:m.private_key,private_key_password:null==r||null==(g=r.ssh_tunnel)?void 0:g.private_key_password,...e}}:a.payload.login_method===ta.Password?{...r,ssh_tunnel:{password:null==r||null==(b=r.ssh_tunnel)?void 0:b.password,...e}}:{...r}}case aa.RemoveSSHTunnelConfig:return{...r,ssh_tunnel:void 0};case aa.AddTableCatalogSheet:return void 0!==r.catalog?{...r,catalog:[...r.catalog,{name:"",value:""}]}:{...r,catalog:[{name:"",value:""}]};case aa.RemoveTableCatalogSheet:return null==(n=r.catalog)||n.splice(a.payload.indexToDelete,1),{...r};case aa.EditorChange:return{...r,[a.payload.name]:a.payload.json};case aa.QueryChange:return{...r,parameters:{...r.parameters,query:Object.fromEntries(new URLSearchParams(a.payload.value))},query_input:a.payload.value};case aa.TextChange:return{...r,[a.payload.name]:a.payload.value};case aa.Fetched:if(d=(null==(i=a.payload)||null==(i=i.parameters)?void 0:i.query)||{},c=Object.entries(d).map((([e,a])=>`${e}=${a}`)).join("&"),a.payload.masked_encrypted_extra&&a.payload.configuration_method===C.DynamicForm){var v;const e=null==(v={...JSON.parse(a.payload.extra||"{}")}.engine_params)?void 0:v.catalog,t=Object.entries(e||{}).map((([e,a])=>({name:e,value:a})));return{...a.payload,engine:a.payload.backend||r.engine,configuration_method:a.payload.configuration_method,catalog:t,parameters:{...a.payload.parameters||r.parameters,catalog:e},query_input:c}}return{...a.payload,masked_encrypted_extra:a.payload.masked_encrypted_extra||"",engine:a.payload.backend||r.engine,configuration_method:a.payload.configuration_method,parameters:a.payload.parameters||r.parameters,ssh_tunnel:a.payload.ssh_tunnel||r.ssh_tunnel,query_input:c};case aa.DbSelected:return{...a.payload,extra:Ge,expose_in_sqllab:!0};case aa.ConfigMethodChange:return{...a.payload};case aa.Reset:default:return null}}const ia=Qe,ra=(0,T.Ay)((({addDangerToast:e,addSuccessToast:a,onDatabaseAdd:t,onHide:n,show:l,databaseId:i,dbEngine:s})=>{var d,m,f,x;const[Y,T]=(0,h.useReducer)(la,null),{state:{loading:P,resource:U,error:I},fetchResource:O,createResource:q,updateResource:H,clearError:R}=(0,M.fn)("database",(0,c.t)("database"),e,"connection"),[V,j]=(0,h.useState)(ia),[K,B]=(0,M.d5)(),[W,le,ie,re,oe,ue]=(0,M.Y8)(),[pe,me]=(0,h.useState)(!1),[_e,xe]=(0,h.useState)(!1),[Se,Ce]=(0,h.useState)(""),[we,Ae]=(0,h.useState)(!1),[Fe,ke]=(0,h.useState)(!1),[De,Ee]=(0,h.useState)(!1),[$e,Te]=(0,h.useState)({}),[Me,Le]=(0,h.useState)({}),[Ue,Oe]=(0,h.useState)({}),[qe,He]=(0,h.useState)({}),[Re,Ve]=(0,h.useState)(!1),[je,Ke]=(0,h.useState)([]),[Ge,ta]=(0,h.useState)(!1),[ra,oa]=(0,h.useState)(),[sa,da]=(0,h.useState)([]),[ca,ha]=(0,h.useState)([]),[ua,pa]=(0,h.useState)([]),[ma,ga]=(0,h.useState)([]),[ba,va]=(0,h.useState)({}),_a=null!=(d=Je.get("ssh_tunnel.form.switch"))?d:Ne,[fa,ya]=(0,h.useState)(void 0);let xa=Je.get("databaseconnection.extraOption");xa&&(xa={...xa,onEdit:e=>{va({...ba,...e})}});const Ya=(0,z.B)(),Sa=(0,M.g9)(),Ca=(0,M.Fp)(),wa=!!i,Aa=Ca||!(null==Y||!Y.engine||!We[Y.engine]),Fa=(null==Y?void 0:Y.configuration_method)===C.SqlalchemyUri,ka=wa||Fa,Da=W||I,Ea=(0,u.W6)(),Na=(null==K||null==(m=K.databases)?void 0:m.find((e=>e.engine===(wa?null==Y?void 0:Y.backend:null==Y?void 0:Y.engine)&&e.default_driver===(null==Y?void 0:Y.driver))))||(null==K||null==(f=K.databases)?void 0:f.find((e=>e.engine===(wa?null==Y?void 0:Y.backend:null==Y?void 0:Y.engine))))||{},$a=e=>{if("database"===e)return(0,c.t)("e.g. world_population")},Ta=(0,h.useCallback)(((e,a)=>{T({type:e,payload:a})}),[]),Ma=(0,h.useCallback)((()=>{ie(null),ue(!1),R()}),[ie,ue]),za=(0,h.useCallback)((({target:e})=>{Ta(aa.ParametersChange,{type:e.type,name:e.name,checked:e.checked,value:e.value})}),[Ta]),La=()=>{T({type:aa.Reset}),me(!1),Ma(),R(),Ae(!1),Ke([]),ta(!1),oa(""),da([]),ha([]),pa([]),ga([]),Te({}),Le({}),Oe({}),He({}),Ve(!1),ya(void 0),n()},Pa=e=>{Ea.push(e)},{state:{alreadyExists:Ua,passwordsNeeded:Ia,sshPasswordNeeded:Oa,sshPrivateKeyNeeded:qa,sshPrivateKeyPasswordNeeded:Ha,loading:Ra,failed:Va},importResource:ja}=(0,M.bN)("database",(0,c.t)("database"),(e=>{oa(e)})),Ka=async()=>{var n,l;let i;if(ke(!0),ue(!1),null==(n=xa)||n.onSave(ba,Y).then((({error:a})=>{a&&(i=a,e(a))})),i)return void ke(!1);const o={...Y||{}};if(o.configuration_method===C.DynamicForm){var s,d;null!=o&&null!=(s=o.parameters)&&s.catalog&&(o.extra=JSON.stringify({...JSON.parse(o.extra||"{}"),engine_params:{catalog:o.parameters.catalog}}));const a=await le(o,!0);if(!r()(W)||null!=a&&a.length)return e((0,c.t)("Connection failed, please check your connection settings.")),void ke(!1);const t=wa?null==(d=o.parameters_schema)?void 0:d.properties:null==Na?void 0:Na.parameters.properties,n=JSON.parse(o.masked_encrypted_extra||"{}");Object.keys(t||{}).forEach((e=>{var a,l,i,r;t[e]["x-encrypted-extra"]&&null!=(a=o.parameters)&&a[e]&&("object"==typeof(null==(l=o.parameters)?void 0:l[e])?(n[e]=null==(i=o.parameters)?void 0:i[e],o.parameters[e]=JSON.stringify(o.parameters[e])):n[e]=JSON.parse((null==(r=o.parameters)?void 0:r[e])||"{}"))})),o.masked_encrypted_extra=JSON.stringify(n),o.engine===w.GSheet&&(o.impersonate_user=!0)}if(null!=o&&null!=(l=o.parameters)&&l.catalog&&(o.extra=JSON.stringify({...JSON.parse(o.extra||"{}"),engine_params:{catalog:o.parameters.catalog}})),!1===fa&&(o.ssh_tunnel=null),null!=Y&&Y.id){if(await H(Y.id,o,o.configuration_method===C.DynamicForm)){var h;if(t&&t(),null==(h=xa)||h.onSave(ba,Y).then((({error:a})=>{a&&(i=a,e(a))})),i)return void ke(!1);we||(La(),a((0,c.t)("Database settings updated")))}}else if(Y){if(await q(o,o.configuration_method===C.DynamicForm)){var u;if(me(!0),t&&t(),null==(u=xa)||u.onSave(ba,Y).then((({error:a})=>{a&&(i=a,e(a))})),i)return void ke(!1);ka&&(La(),a((0,c.t)("Database connected")))}}else{if(ta(!0),!(je[0].originFileObj instanceof File))return;await ja(je[0].originFileObj,$e,Me,Ue,qe,Re)&&(t&&t(),La(),a((0,c.t)("Database connected")))}xe(!0),Ae(!1),ke(!1)},Ba=e=>{if("Other"===e)T({type:aa.DbSelected,payload:{database_name:e,configuration_method:C.SqlalchemyUri,engine:void 0,engine_information:{supports_file_upload:!0}}});else{const a=null==K?void 0:K.databases.filter((a=>a.name===e))[0],{engine:t,parameters:n,engine_information:l,default_driver:i,sqlalchemy_uri_placeholder:r}=a,o=void 0!==n;T({type:aa.DbSelected,payload:{database_name:e,engine:t,configuration_method:o?C.DynamicForm:C.SqlalchemyUri,engine_information:l,driver:i,sqlalchemy_uri_placeholder:r}}),t===w.GSheet&&T({type:aa.AddTableCatalogSheet})}},Ja=()=>{U&&O(U.id),xe(!1),Ae(!0)},Ga=()=>{Ma(),we&&me(!1),Ge&&ta(!1),Va&&(ta(!1),oa(""),da([]),ha([]),pa([]),ga([]),Te({}),Le({}),Oe({}),He({})),T({type:aa.Reset}),Ke([])},Qa=()=>Y?!pe||we?(0,o.FD)(o.FK,{children:[(0,o.Y)(be,{onClick:Ga,buttonStyle:"secondary",children:(0,c.t)("Back")},"back"),(0,o.Y)(be,{buttonStyle:"primary",onClick:Ka,loading:Fe,disabled:!!(!oe||re||W&&Object.keys(W).length>0),children:(0,c.t)("Connect")},"submit")]}):(0,o.FD)(o.FK,{children:[(0,o.Y)(be,{onClick:Ja,children:(0,c.t)("Back")},"back"),(0,o.Y)(be,{buttonStyle:"primary",onClick:Ka,loading:Fe,children:(0,c.t)("Finish")},"submit")]}):Ge?(0,o.FD)(o.FK,{children:[(0,o.Y)(be,{onClick:Ga,children:(0,c.t)("Back")},"back"),(0,o.Y)(be,{buttonStyle:"primary",onClick:Ka,disabled:!!(Ra||Ua.length&&!Re||Ia.length&&"{}"===JSON.stringify($e)||Oa.length&&"{}"===JSON.stringify(Me)||qa.length&&"{}"===JSON.stringify(Ue)||Ha.length&&"{}"===JSON.stringify(qe)),loading:Fe,children:(0,c.t)("Connect")},"submit")]}):(0,o.Y)(o.FK,{}),Wa=(0,h.useRef)(!0);(0,h.useEffect)((()=>{Wa.current?Wa.current=!1:Ra||Ua.length||Ia.length||Oa.length||qa.length||Ha.length||Fe||Va||(La(),a((0,c.t)("Database connected")))}),[Ua,Ia,Ra,Va,Oa,qa,Ha]),(0,h.useEffect)((()=>{l&&(j(ia),ke(!0),B()),i&&l&&wa&&i&&(P||O(i).catch((a=>e((0,c.t)("Sorry there was an error fetching database information: %s",a.message)))))}),[l,i]),(0,h.useEffect)((()=>{U&&(T({type:aa.Fetched,payload:U}),Ce(U.database_name))}),[U]),(0,h.useEffect)((()=>{Fe&&ke(!1),K&&s&&Ba(s)}),[K]),(0,h.useEffect)((()=>{var e;Ge&&(null==(e=document)||e.getElementsByClassName("ant-upload-list-item-name")[0].scrollIntoView())}),[Ge]),(0,h.useEffect)((()=>{da([...Ia])}),[Ia]),(0,h.useEffect)((()=>{ha([...Oa])}),[Oa]),(0,h.useEffect)((()=>{pa([...qa])}),[qa]),(0,h.useEffect)((()=>{ga([...Ha])}),[Ha]),(0,h.useEffect)((()=>{var e;void 0!==(null==Y||null==(e=Y.parameters)?void 0:e.ssh)&&ya(Y.parameters.ssh)}),[null==Y||null==(x=Y.parameters)?void 0:x.ssh]);const Xa=()=>ra?(0,o.Y)(ae,{children:(0,o.Y)($.$p,{message:ra})}):null,Za=e=>{var a,t;const n=null!=(a=null==(t=e.currentTarget)?void 0:t.value)?a:"";Ve(n.toUpperCase()===(0,c.t)("OVERWRITE"))},et=()=>{let e=[];var a;return r()(I)?r()(W)||"GENERIC_DB_ENGINE_ERROR"!==(null==W?void 0:W.error_type)||(e=[(null==W?void 0:W.description)||(null==W?void 0:W.message)]):e="object"==typeof I?Object.values(I):"string"==typeof I?[I]:[],e.length?(0,o.Y)(Ze,{children:(0,o.Y)($.x6,{title:(0,c.t)("Database Creation Error"),subtitle:(0,c.t)("We are unable to connect to your database."),descriptionDetails:(null==(a=e)?void 0:a[0])||(null==W?void 0:W.description),copyText:null==W?void 0:W.description})}):(0,o.Y)(o.FK,{})},at=()=>{ke(!0),O(null==U?void 0:U.id).then((e=>{(0,p.SO)(p.Hh.Database,e)}))},tt=()=>(0,o.Y)(Be,{db:Y,onSSHTunnelParametersChange:({target:e})=>{Ta(aa.ParametersSSHTunnelChange,{type:e.type,name:e.name,value:e.value}),Ma()},setSSHTunnelLoginMethod:e=>T({type:aa.SetSSHTunnelLoginMethod,payload:{login_method:e}})}),nt=()=>(0,o.FD)(o.FK,{children:[(0,o.Y)(ze,{isValidating:re,isEditMode:wa,db:Y,sslForced:!1,dbModel:Na,onAddTableCatalog:()=>{T({type:aa.AddTableCatalogSheet})},onQueryChange:({target:e})=>Ta(aa.QueryChange,{name:e.name,value:e.value}),onExtraInputChange:({target:e})=>Ta(aa.ExtraInputChange,{name:e.name,value:e.value}),onEncryptedExtraInputChange:({target:e})=>Ta(aa.EncryptedExtraInputChange,{name:e.name,value:e.value}),onRemoveTableCatalog:e=>{T({type:aa.RemoveTableCatalogSheet,payload:{indexToDelete:e}})},onParametersChange:za,onChange:({target:e})=>Ta(aa.TextChange,{name:e.name,value:e.value}),getValidation:()=>le(Y),validationErrors:W,getPlaceholder:$a,clearValidationErrors:Ma}),fa&&(0,o.Y)(ea,{children:tt()})]});if(je.length>0&&(Ua.length||sa.length||ca.length||ua.length||ma.length))return(0,o.FD)(k.aF,{centered:!0,css:e=>[G,Z(e),te(e),ne(e)],footer:Qa(),maskClosable:!1,name:"database",onHide:La,onHandledPrimaryAction:Ka,primaryButtonName:(0,c.t)("Connect"),show:l,title:(0,o.Y)(L.r,{title:(0,c.t)("Connect a database"),icon:(0,o.Y)(y.F.InsertRowAboveOutlined,{})}),width:"500px",children:[(0,o.Y)(Ie,{db:Y,dbName:Se,dbModel:Na,fileList:je,hasConnectedDb:pe,isEditMode:wa,isLoading:Fe,useSqlAlchemyForm:Fa}),Ua.length?(0,o.FD)(o.FK,{children:[(0,o.Y)(ae,{children:(0,o.Y)(v.F,{closable:!1,css:e=>(e=>_.AH`
  margin: ${4*e.sizeUnit}px 0;

  .ant-alert-message {
    margin: 0;
  }
`)(e),type:"warning",showIcon:!0,message:"",description:(0,c.t)("You are importing one or more databases that already exist. Overwriting might cause you to lose some of your work. Are you sure you want to overwrite?")})}),(0,o.Y)(A.M,{id:"confirm_overwrite",name:"confirm_overwrite",isValidating:re,required:!0,validationMethods:{onBlur:()=>{}},errorMessage:null==W?void 0:W.confirm_overwrite,label:(0,c.t)('Type "%s" to confirm',(0,c.t)("OVERWRITE")),onChange:Za,css:X})]}):null,Xa(),sa.length||ca.length||ua.length||ma.length?[...new Set([...sa,...ca,...ua,...ma])].map((e=>(0,o.FD)(o.FK,{children:[(0,o.Y)(ae,{children:(0,o.Y)(v.F,{closable:!1,css:e=>ee(e),type:"info",showIcon:!0,message:"Database passwords",description:(0,c.t)('The passwords for the databases below are needed in order to import them. Please note that the "Secure Extra" and "Certificate" sections of the database configuration are not present in explore files and should be added manually after the import if they are needed.')})}),(null==sa?void 0:sa.indexOf(e))>=0&&(0,o.Y)(A.M,{id:"password_needed",name:"password_needed",required:!0,value:$e[e],onChange:a=>Te({...$e,[e]:a.target.value}),isValidating:re,validationMethods:{onBlur:()=>{}},errorMessage:null==W?void 0:W.password_needed,label:(0,c.t)("%s PASSWORD",e.slice(10)),css:X}),(null==ca?void 0:ca.indexOf(e))>=0&&(0,o.Y)(A.M,{isValidating:re,id:"ssh_tunnel_password_needed",name:"ssh_tunnel_password_needed",required:!0,value:Me[e],onChange:a=>Le({...Me,[e]:a.target.value}),validationMethods:{onBlur:()=>{}},errorMessage:null==W?void 0:W.ssh_tunnel_password_needed,label:(0,c.t)("%s SSH TUNNEL PASSWORD",e.slice(10)),css:X}),(null==ua?void 0:ua.indexOf(e))>=0&&(0,o.Y)(A.M,{id:"ssh_tunnel_private_key_needed",name:"ssh_tunnel_private_key_needed",isValidating:re,required:!0,value:Ue[e],onChange:a=>Oe({...Ue,[e]:a.target.value}),validationMethods:{onBlur:()=>{}},errorMessage:null==W?void 0:W.ssh_tunnel_private_key_needed,label:(0,c.t)("%s SSH TUNNEL PRIVATE KEY",e.slice(10)),css:X}),(null==ma?void 0:ma.indexOf(e))>=0&&(0,o.Y)(A.M,{id:"ssh_tunnel_private_key_password_needed",name:"ssh_tunnel_private_key_password_needed",isValidating:re,required:!0,value:qe[e],onChange:a=>He({...qe,[e]:a.target.value}),validationMethods:{onBlur:()=>{}},errorMessage:null==W?void 0:W.ssh_tunnel_private_key_password_needed,label:(0,c.t)("%s SSH TUNNEL PRIVATE KEY PASSWORD",e.slice(10)),css:X})]}))):null]});const lt=wa?(e=>(0,o.FD)(o.FK,{children:[(0,o.Y)(be,{onClick:La,buttonStyle:"secondary",children:(0,c.t)("Close")},"close"),(0,o.Y)(be,{buttonStyle:"primary",onClick:Ka,disabled:null==e?void 0:e.is_managed_externally,loading:Fe,tooltip:null!=e&&e.is_managed_externally?(0,c.t)("This database is managed externally, and can't be edited in Superset"):"",children:(0,c.t)("Finish")},"submit")]}))(Y):Qa();return ka?(0,o.FD)(k.aF,{css:e=>[J,G,Z(e),te(e),ne(e)],name:"database",onHandledPrimaryAction:Ka,onHide:La,primaryButtonName:wa?(0,c.t)("Save"):(0,c.t)("Connect"),width:"500px",centered:!0,show:l,title:(0,o.Y)(L.r,{isEditMode:wa,title:wa?(0,c.t)("Edit database"):(0,c.t)("Connect a database"),icon:wa?(0,o.Y)(y.F.EditOutlined,{iconSize:"l"}):(0,o.Y)(y.F.InsertRowAboveOutlined,{iconSize:"l"})}),footer:lt,maskClosable:!1,children:[(0,o.Y)(ve,{children:(0,o.Y)(he,{children:(0,o.Y)(Ie,{isLoading:Fe,isEditMode:wa,useSqlAlchemyForm:Fa,hasConnectedDb:pe,db:Y,dbName:Se,dbModel:Na})})}),(0,o.Y)(Xe,{defaultActiveKey:ia,activeKey:V,onTabClick:e=>j(e),animated:{inkBar:!0,tabPane:!0},items:[{key:Qe,label:(0,o.Y)("span",{children:(0,c.t)("Basic")}),children:(0,o.FD)(o.FK,{children:[Fa?(0,o.FD)(se,{children:[(0,o.FD)(Ye,{db:Y,onInputChange:({target:e})=>{ue(!1),Ta(aa.InputChange,{type:e.type,name:e.name,checked:e.checked,value:e.value})},conf:Ya,testConnection:()=>{var t;if(Ma(),null==Y||!Y.sqlalchemy_uri)return void e((0,c.t)("Please enter a SQLAlchemy URI to test"));const n={sqlalchemy_uri:(null==Y?void 0:Y.sqlalchemy_uri)||"",database_name:(null==Y||null==(t=Y.database_name)?void 0:t.trim())||void 0,impersonate_user:(null==Y?void 0:Y.impersonate_user)||void 0,extra:null==Y?void 0:Y.extra,masked_encrypted_extra:(null==Y?void 0:Y.masked_encrypted_extra)||"",server_cert:(null==Y?void 0:Y.server_cert)||void 0,ssh_tunnel:!r()(null==Y?void 0:Y.ssh_tunnel)&&fa?{...Y.ssh_tunnel,server_port:Number(Y.ssh_tunnel.server_port)}:void 0};Ee(!0),(0,M.ym)(n,(a=>{Ee(!1),e(a),ue(!1)}),(e=>{Ee(!1),a(e),ue(!0)}))},testInProgress:De,children:[(0,o.Y)(_a,{dbModel:Na,db:Y,changeMethods:{onParametersChange:za},clearValidationErrors:Ma}),fa&&tt()]}),(ot=(null==Y?void 0:Y.backend)||(null==Y?void 0:Y.engine),void 0!==(null==K||null==(st=K.databases)||null==(st=st.find((e=>e.backend===ot||e.engine===ot)))?void 0:st.parameters)&&!wa&&(0,o.FD)("div",{css:e=>Q(e),children:[(0,o.Y)(F.$,{buttonStyle:"link",onClick:()=>T({type:aa.ConfigMethodChange,payload:{database_name:null==Y?void 0:Y.database_name,configuration_method:C.DynamicForm,engine:null==Y?void 0:Y.engine}}),css:e=>(e=>_.AH`
  text-transform: initial;
  padding: ${8*e.sizeUnit}px 0 0;
  margin-left: 0px;
`)(e),children:(0,c.t)("Connect this database using the dynamic form instead")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("Click this link to switch to an alternate form that exposes only the required fields needed to connect this database.")})]}))]}):nt(),!wa&&(0,o.Y)(ae,{children:(0,o.Y)(v.F,{closable:!1,css:e=>ee(e),message:(0,c.t)("Additional fields may be required"),showIcon:!0,description:(0,o.FD)(o.FK,{children:[(0,c.t)("Select databases require additional fields to be completed in the Advanced tab to successfully connect the database. Learn what requirements your databases has "),(0,o.Y)("a",{href:Pe,target:"_blank",rel:"noopener noreferrer",className:"additional-fields-alert-description",children:(0,c.t)("here")}),"."]}),type:"info"})}),Da&&et()]})},{key:"advanced",label:(0,o.Y)("span",{children:(0,c.t)("Advanced")}),children:(0,o.Y)(ye,{extraExtension:xa,db:Y,onInputChange:e=>{const{target:a}=e;Ta(aa.InputChange,{type:a.type,name:a.name,checked:a.checked,value:a.value})},onTextChange:({target:e})=>{Ta(aa.TextChange,{name:e.name,value:e.value})},onEditorChange:e=>{Ta(aa.EditorChange,e)},onExtraInputChange:e=>{const{target:a}=e;Ta(aa.ExtraInputChange,{type:a.type,name:a.name,checked:a.checked,value:a.value})},onExtraEditorChange:e=>{Ta(aa.ExtraEditorChange,e)}})}]})]}):(0,o.FD)(k.aF,{css:e=>[G,Z(e),te(e),ne(e)],name:"database",onHandledPrimaryAction:Ka,onHide:La,primaryButtonName:pe?(0,c.t)("Finish"):(0,c.t)("Connect"),width:"500px",centered:!0,show:l,title:(0,o.Y)(L.r,{title:(0,c.t)("Connect a database"),icon:(0,o.Y)(y.F.InsertRowAboveOutlined,{})}),footer:Qa(),maskClosable:!1,children:[!Fe&&pe?(0,o.FD)(o.FK,{children:[(0,o.Y)(Ie,{isLoading:Fe,isEditMode:wa,useSqlAlchemyForm:Fa,hasConnectedDb:pe,db:Y,dbName:Se,dbModel:Na,editNewDb:we}),_e&&(0,o.FD)(na,{children:[(0,o.Y)(F.$,{buttonStyle:"secondary",onClick:()=>{ke(!0),at(),Pa("/dataset/add/")},children:(0,c.t)("Create dataset")}),(0,o.Y)(F.$,{buttonStyle:"secondary",onClick:()=>{ke(!0),at(),Pa("/sqllab?db=true")},children:(0,c.t)("Query data in SQL Lab")})]}),we?nt():(0,o.Y)(ye,{extraExtension:xa,db:Y,onInputChange:e=>{const{target:a}=e;Ta(aa.InputChange,{type:a.type,name:a.name,checked:"checked"in a&&a.checked,value:a.value})},onTextChange:({target:e})=>Ta(aa.TextChange,{name:e.name,value:e.value}),onEditorChange:e=>Ta(aa.EditorChange,e),onExtraInputChange:e=>{const{target:a}=e;Ta(aa.ExtraInputChange,{type:a.type,name:a.name,checked:"checked"in a&&a.checked,value:a.value})},onExtraEditorChange:e=>Ta(aa.ExtraEditorChange,e)})]}):(0,o.Y)(o.FK,{children:!Fe&&(Y?(0,o.FD)(o.FK,{children:[(0,o.Y)(Ie,{isLoading:Fe,isEditMode:wa,useSqlAlchemyForm:Fa,hasConnectedDb:pe,db:Y,dbName:Se,dbModel:Na}),Aa&&(()=>{var e,a,t,n,l;const{hostname:i}=window.location;let r=(null==Ca||null==(e=Ca.REGIONAL_IPS)?void 0:e.default)||"";const s=(null==Ca?void 0:Ca.REGIONAL_IPS)||{};return Object.entries(s).forEach((([e,a])=>{const t=new RegExp(e);i.match(t)&&(r=a)})),(null==Y?void 0:Y.engine)&&(0,o.Y)(ae,{children:(0,o.Y)(v.F,{closable:!1,css:e=>ee(e),type:"info",showIcon:!0,message:(null==(a=We[Y.engine])?void 0:a.message)||(null==Ca||null==(t=Ca.DEFAULT)?void 0:t.message),description:(null==(n=We[Y.engine])?void 0:n.description)||(null==Ca||null==(l=Ca.DEFAULT)?void 0:l.description)+r})})})(),nt(),(0,o.Y)("div",{css:e=>Q(e),children:Na.engine!==w.GSheet&&(0,o.FD)(o.FK,{children:[(0,o.Y)(F.$,{buttonStyle:"link",onClick:()=>{Ma(),T({type:aa.ConfigMethodChange,payload:{engine:Y.engine,configuration_method:C.SqlalchemyUri,database_name:Y.database_name}})},css:de,children:(0,c.t)("Connect this database with a SQLAlchemy URI string instead")}),(0,o.Y)(D.I,{tooltip:(0,c.t)("Click this link to switch to an alternate form that allows you to input the SQLAlchemy URL for this database manually.")})]})}),Da&&et()]}):(0,o.FD)(ge,{children:[(0,o.Y)(Ie,{isLoading:Fe,isEditMode:wa,useSqlAlchemyForm:Fa,hasConnectedDb:pe,db:Y,dbName:Se,dbModel:Na}),(0,o.Y)("div",{className:"preferred",children:null==K||null==(rt=K.databases)?void 0:rt.filter((e=>e.preferred)).map((e=>(0,o.Y)(S,{className:"preferred-item",onClick:()=>Ba(e.name),buttonText:e.name,icon:null==Sa?void 0:Sa[e.engine]},`${e.name}`)))}),(0,o.FD)("div",{className:"available",children:[(0,o.Y)("h4",{className:"available-label",children:(0,c.t)("Or choose from a list of other databases we support:")}),(0,o.Y)(g.l,{className:"control-label",children:(0,c.t)("Supported databases")}),(0,o.Y)(b.A,{className:"available-select",onChange:Ba,placeholder:(0,c.t)("Choose a database..."),options:[...((null==K?void 0:K.databases)||[]).map(((e,a)=>({value:e.name,label:e.name,key:`database-${a}`}))),{value:"Other",label:(0,c.t)("Other"),key:"Other"}],showSearch:!0,sortComparator:(e,a)=>"Other"===e.value?1:"Other"===a.value?-1:String(e.label).localeCompare(String(a.label)),getPopupContainer:e=>e.parentElement||document.body,dropdownStyle:{maxHeight:400,overflow:"auto"}}),(0,o.Y)(v.F,{showIcon:!0,closable:!1,css:e=>ee(e),type:"info",message:(null==Ca||null==(it=Ca.ADD_DATABASE)?void 0:it.message)||(0,c.t)("Want to add a new database?"),description:null!=Ca&&Ca.ADD_DATABASE?(0,o.FD)(o.FK,{children:[(0,c.t)("Any databases that allow connections via SQL Alchemy URIs can be added. "),(0,o.Y)("a",{href:null==Ca?void 0:Ca.ADD_DATABASE.contact_link,target:"_blank",rel:"noopener noreferrer",children:null==Ca?void 0:Ca.ADD_DATABASE.contact_description_link})," ",null==Ca?void 0:Ca.ADD_DATABASE.description]}):(0,o.FD)(o.FK,{children:[(0,c.t)("Any databases that allow connections via SQL Alchemy URIs can be added. Learn about how to connect a database driver "),(0,o.Y)("a",{href:Pe,target:"_blank",rel:"noopener noreferrer",children:(0,c.t)("here")}),"."]})})]}),(0,o.Y)(fe,{children:(0,o.Y)(E.A,{name:"databaseFile",id:"databaseFile",accept:".yaml,.json,.yml,.zip",customRequest:()=>{},onChange:async e=>{oa(""),da([]),ha([]),pa([]),ga([]),Te({}),Le({}),Oe({}),He({}),ta(!0),Ke([{...e.file,status:"done"}]),e.file.originFileObj instanceof File&&await ja(e.file.originFileObj,$e,Me,Ue,qe,Re)&&(null==t||t())},onRemove:e=>(Ke(je.filter((a=>a.uid!==e.uid))),!1),children:(0,o.Y)(F.$,{buttonStyle:"link",css:ce,children:(0,c.t)("Import database from file")})})}),Xa()]}))}),Fe&&(0,o.Y)(N.R,{})]});var it,rt,ot,st}))},14180:(e,a,t)=>{t.d(a,{A:()=>Q});var n=t(2445),l=t(96540),i=t(79378),r=t(59744),o=t(74098),s=t(65729),d=t(97163),c=t(43303),h=t(42566),u=t(47152),p=t(16370),m=t(77829),g=t(88217),b=t(49965),v=t(17355),_=t(2801),f=t(7142),y=t(15039),x=t(8558),Y=t(58561),S=t.n(Y),C=t(64457),w=t(51692),A=t(82384),F=t(50290),k=t(17437);const D=(0,F.I4)(A.e)`
  ${({theme:e})=>k.AH`
    flex: 1;
    margin-top: 0;
    margin-bottom: ${2.5*e.sizeUnit}px;
  }
  `}
`,E=F.I4.div`
  display: flex;
  align-items: center;
  margin-top: 0;
`,N=k.AH`
  .ant-modal-body {
    padding-left: 0;
    padding-right: 0;
    padding-top: 0;
  }
`,$=e=>k.AH`
  .switch-label {
    color: ${e.colorTextSecondary};
    margin-left: ${4*e.sizeUnit}px;
  }
`,T=e=>k.AH`
  .ant-modal-header {
    padding: ${4.5*e.sizeUnit}px ${4*e.sizeUnit}px
      ${4*e.sizeUnit}px;
  }

  .ant-modal-close-x .close {
    opacity: 1;
  }

  .ant-modal-body {
    height: ${180.5*e.sizeUnit}px;
  }

  .ant-modal-footer {
    height: ${16.25*e.sizeUnit}px;
  }

  .info-solid-small {
    vertical-align: bottom;
  }
`;var M=t(89232);const z=F.I4.div`
  //margin-top: 10px;
  //margin-bottom: 10px;
`,L=({columns:e,maxColumnsToShow:a=4})=>{const t=e.map((e=>({name:e})));return(0,n.FD)(z,{children:[(0,n.Y)(h.o.Text,{type:"secondary",children:"Columns:"}),0===e.length?(0,n.Y)("p",{className:"help-block",children:(0,o.t)("Upload file to preview columns")}):(0,n.Y)(M.Sk,{tags:t,maxTags:a})]})};var P=t(5250);const U=({label:e,tip:a,children:t,name:l,rules:i})=>(0,n.Y)(D,{label:(0,n.FD)("div",{children:[e,(0,n.Y)(P.I,{tooltip:a})]}),name:l,rules:i,children:t}),I=["delimiter","skip_initial_space","skip_blank_lines","day_first","column_data_types","column_dates","decimal_character","null_values","index_column","header_row","rows_to_read","skip_rows"],O=["sheet_name","column_dates","decimal_character","null_values","index_column","header_row","rows_to_read","skip_rows"],q=[],H=["rows_to_read","index_column"],R=[...I,...O,...q],V={csv:I,excel:O,columnar:q},j=(e,a)=>V[a].includes(e),K={table_name:"",schema:"",sheet_name:void 0,delimiter:",",already_exists:"fail",skip_initial_space:!1,skip_blank_lines:!1,day_first:!1,decimal_character:".",null_values:[],header_row:"0",rows_to_read:null,skip_rows:"0",column_dates:[],index_column:null,dataframe_index:!1,index_label:"",columns_read:[],column_data_types:""},B={csv:".csv, .tsv",excel:".xls, .xlsx",columnar:".parquet, .zip"},J={csv:"CSV",excel:"Excel",columnar:"Columnar"},G=({label:e,dataTest:a,children:t,...l})=>(0,n.FD)(E,{children:[(0,n.Y)(y.A,{...l}),(0,n.Y)("div",{className:"switch-label",children:e}),t]}),Q=(0,C.Ay)((({addDangerToast:e,addSuccessToast:a,onHide:t,show:y,allowedExtensions:Y,type:C="csv"})=>{const[A]=s.l.useForm(),[F,k]=(0,l.useState)(0),[E,M]=(0,l.useState)([]),[z,P]=(0,l.useState)([]),[I,O]=(0,l.useState)([]),[q,Q]=(0,l.useState)({}),[W,X]=(0,l.useState)(","),[Z,ee]=(0,l.useState)(!1),[ae,te]=(0,l.useState)(),[ne,le]=(0,l.useState)(!1),[ie,re]=(0,l.useState)(!0),[oe,se]=(0,l.useState)(!1),[de,ce]=(0,l.useState)("general"),he=(0,l.useMemo)((()=>(e="",a,t)=>{const n=S().encode_uri({filters:[{col:"allow_file_upload",opr:"eq",value:!0}],page:a,page_size:t});return i.A.get({endpoint:`/api/v1/database/?q=${n}`}).then((e=>({data:e.json.result.map((e=>({value:e.id,label:e.database_name}))),totalCount:e.json.count})))}),[]),ue=(0,l.useMemo)((()=>(e="",a,t)=>F?i.A.get({endpoint:`/api/v1/database/${F}/schemas/?q=(upload_allowed:!t)`}).then((e=>({data:e.json.result.map((e=>({value:e,label:e}))),totalCount:e.json.count}))):Promise.resolve({data:[],totalCount:0})),[F]),pe=a=>{const t=A.getFieldsValue(),n={...K,...t},l=new FormData;return l.append("file",a),"csv"===C&&l.append("delimiter",n.delimiter),l.append("type",C),se(!0),i.A.post({endpoint:"/api/v1/database/upload_metadata/",body:l,headers:{Accept:"application/json"}}).then((e=>{const{items:a}=e.json.result;if(a&&"excel"!==C)P(a[0].column_names);else{const{allSheetNames:e,sheetColumnNamesMap:t}=a.reduce(((e,a)=>(e.allSheetNames.push(a.sheet_name),e.sheetColumnNamesMap[a.sheet_name]=a.column_names,e)),{allSheetNames:[],sheetColumnNamesMap:{}});P(a[0].column_names),O(e),A.setFieldsValue({sheet_name:e[0]}),Q(t)}})).catch((a=>(0,r.h4)(a).then((a=>{e(a.error||"Error"),P([]),A.setFieldsValue({sheet_name:void 0}),O([])})))).finally((()=>{se(!1)}))},me=()=>{M([]),P([]),te(""),k(0),O([]),ee(!1),X(","),re(!0),se(!1),Q({}),A.resetFields(),t()},ge=()=>z.map((e=>({value:e,label:e})));(0,l.useEffect)((()=>{if(z.length>0&&E[0].originFileObj&&E[0].originFileObj instanceof File){if(!ie)return;pe(E[0].originFileObj).then((e=>e))}}),[W]),(0,l.useEffect)((()=>{y&&ce("general")}),[y]);const be={csv:(0,o.t)("CSV upload"),excel:(0,o.t)("Excel upload"),columnar:(0,o.t)("Columnar upload")};return(0,n.Y)(d.aF,{css:e=>[N,T(e),$(e)],primaryButtonLoading:Z,name:"database",onHandledPrimaryAction:A.submit,onHide:me,width:"500px",primaryButtonName:(0,o.t)("Upload"),centered:!0,show:y,title:(0,n.Y)((()=>{const e=be[C]||(0,o.t)("Upload");return(0,n.Y)(w.r,{title:e})}),{}),children:(0,n.Y)(s.l,{form:A,onFinish:()=>{var t;const n=A.getFieldsValue();delete n.database,n.schema=ae;const l={...K,...n},s=new FormData,d=null==(t=E[0])?void 0:t.originFileObj;d&&s.append("file",d),((e,a)=>{const t=(()=>{const e=V[C]||[];return[...R].filter((a=>!e.includes(a)))})();Object.entries(a).forEach((([a,n])=>{t.includes(a)||H.includes(a)&&null==n||e.append(a,n)}))})(s,l),ee(!0);const c=`/api/v1/database/${F}/upload/`;return s.append("type",C),i.A.post({endpoint:c,body:s,headers:{Accept:"application/json"}}).then((()=>{a((0,o.t)("Data imported")),ee(!1),me()})).catch((a=>(0,r.h4)(a).then((a=>{e(a.error||"Error")})))).finally((()=>{ee(!1)}))},layout:"vertical",initialValues:K,children:(0,n.Y)(c.S,{expandIconPosition:"end",accordion:!0,activeKey:de,onChange:e=>ce(e),defaultActiveKey:"general",modalMode:!0,items:[{key:"general",label:(0,n.Y)(h.o.Text,{strong:!0,children:(0,o.t)("General information")}),children:(0,n.FD)(n.FK,{children:[(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(D,{label:(0,o.t)("%(label)s file",{label:J[C]}),name:"file",required:!0,rules:[{validator:(e,a)=>0===E.length?Promise.reject((0,o.t)("Uploading a file is required")):((e,a)=>{const t=e.name.match(/.+\.([^.]+)$/);if(!t)return!1;const n=t[1].toLowerCase();return a.map((e=>e.toLowerCase())).includes(n)})(E[0],Y)?Promise.resolve():Promise.reject((0,o.t)("Upload a file with a valid extension. Valid: [%s]",Y.join(",")))}],children:(0,n.Y)(m.A,{name:"modelFile",id:"modelFile",accept:B[C],fileList:E,onChange:async e=>{M([{...e.file,status:"done"}]),ie&&await pe(e.file.originFileObj)},onRemove:e=>(M(E.filter((a=>a.uid!==e.uid))),P([]),O([]),A.setFieldsValue({sheet_name:void 0}),!1),customRequest:()=>{},children:(0,n.Y)(g.$,{"aria-label":(0,o.t)("Select"),icon:(0,n.Y)(x.F.UploadOutlined,{}),loading:oe,children:(0,o.t)("Select")})})})})}),(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(D,{children:(0,n.Y)(G,{label:(0,o.t)("Preview uploaded file"),dataTest:"previewUploadedFile",onChange:e=>{re(e)},checked:ie})})})}),ie&&(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(L,{columns:z})})}),(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(D,{label:(0,o.t)("Database"),required:!0,name:"database",rules:[{validator:(e,a)=>F?Promise.resolve():Promise.reject((0,o.t)("Selecting a database is required"))}],children:(0,n.Y)(b.A,{ariaLabel:(0,o.t)("Select a database"),options:he,onChange:e=>{k(null==e?void 0:e.value),te(void 0),A.setFieldsValue({schema:void 0})},allowClear:!0,placeholder:(0,o.t)("Select a database to upload the file to")})})})}),(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(D,{label:(0,o.t)("Schema"),name:"schema",children:(0,n.Y)(b.A,{ariaLabel:(0,o.t)("Select a schema"),options:ue,onChange:e=>{te(null==e?void 0:e.value)},allowClear:!0,placeholder:(0,o.t)("Select a schema if the database supports this")})})})}),(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(D,{label:(0,o.t)("Table name"),name:"table_name",required:!0,rules:[{required:!0,message:"Table name is required"}],children:(0,n.Y)(v.A,{"aria-label":(0,o.t)("Table Name"),name:"table_name",type:"text",placeholder:(0,o.t)("Name of table to be created")})})})}),j("delimiter",C)&&(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(U,{label:(0,o.t)("Delimiter"),tip:(0,o.t)("Select a delimiter for this data"),name:"delimiter",children:(0,n.Y)(_.A,{ariaLabel:(0,o.t)("Choose a delimiter"),options:[{value:",",label:'Comma ","'},{value:";",label:'Semicolon ";"'},{value:"\t",label:'Tab "\\t"'},{value:"|",label:"Pipe"}],onChange:e=>{X(e)},allowNewOptions:!0})})})}),j("sheet_name",C)&&(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(D,{label:(0,o.t)("Sheet name"),name:"sheet_name",children:(0,n.Y)(_.A,{ariaLabel:(0,o.t)("Choose sheet name"),options:I.map((e=>({value:e,label:e}))),onChange:e=>{var a;P(null!=(a=q[e])?a:[])},allowNewOptions:!0,placeholder:(0,o.t)("Select a sheet name from the uploaded file")})})})})]})},{key:"file-settings",label:(0,n.Y)(h.o.Text,{strong:!0,children:(0,o.t)("File settings")}),children:(0,n.FD)(n.FK,{children:[(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(U,{label:(0,o.t)("If table already exists"),tip:(0,o.t)("What should happen if the table already exists"),name:"already_exists",children:(0,n.Y)(_.A,{ariaLabel:(0,o.t)("Choose already exists"),options:[{value:"fail",label:"Fail"},{value:"replace",label:"Replace"},{value:"append",label:"Append"}],onChange:()=>{}})})})}),j("column_dates",C)&&(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(D,{label:(0,o.t)("Columns to be parsed as dates"),name:"column_dates",children:(0,n.Y)(_.A,{ariaLabel:(0,o.t)("Choose columns to be parsed as dates"),mode:"multiple",options:ge(),allowClear:!0,allowNewOptions:!0,placeholder:(0,o.t)("A comma separated list of columns that should be parsed as dates")})})})}),j("decimal_character",C)&&(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(U,{label:(0,o.t)("Decimal character"),tip:(0,o.t)("Character to interpret as decimal point"),name:"decimal_character",children:(0,n.Y)(v.A,{type:"text"})})})}),j("null_values",C)&&(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(U,{label:(0,o.t)("Null Values"),tip:(0,o.t)("Choose values that should be treated as null. Warning: Hive database supports only a single value"),name:"null_values",children:(0,n.Y)(_.A,{mode:"multiple",options:[{value:'""',label:'Empty Strings ""'},{value:"None",label:"None"},{value:"nan",label:"nan"},{value:"null",label:"null"},{value:"N/A",label:"N/A"}],allowClear:!0,allowNewOptions:!0})})})}),j("skip_initial_space",C)&&(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(D,{name:"skip_initial_space",children:(0,n.Y)(G,{label:(0,o.t)("Skip spaces after delimiter"),dataTest:"skipInitialSpace"})})})}),j("skip_blank_lines",C)&&(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(D,{name:"skip_blank_lines",children:(0,n.Y)(G,{label:(0,o.t)("Skip blank lines rather than interpreting them as Not A Number values"),dataTest:"skipBlankLines"})})})}),j("day_first",C)&&(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(D,{name:"day_first",children:(0,n.Y)(G,{label:(0,o.t)("DD/MM format dates, international and European format"),dataTest:"dayFirst"})})})})]})},{key:"columns",label:(0,n.Y)(h.o.Text,{strong:!0,children:(0,o.t)("Columns")}),children:(0,n.FD)(n.FK,{children:[(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(D,{label:(0,o.t)("Columns to read"),name:"columns_read",children:(0,n.Y)(_.A,{ariaLabel:(0,o.t)("Choose columns to read"),mode:"multiple",options:ge(),allowClear:!0,allowNewOptions:!0,placeholder:(0,o.t)("List of the column names that should be read")})})})}),j("column_data_types",C)&&(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(U,{label:(0,o.t)("Column data types"),tip:(0,o.t)('A dictionary with column names and their data types if you need to change the defaults. Example: {"user_id":"int"}. Check Python\'s Pandas library for supported data types.'),name:"column_data_types",children:(0,n.Y)(v.A,{"aria-label":(0,o.t)("Column data types"),type:"text"})})})}),(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(D,{name:"dataframe_index",children:(0,n.Y)(G,{label:(0,o.t)("Create dataframe index"),dataTest:"dataFrameIndex",onChange:le})})})}),ne&&j("index_column",C)&&(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(U,{label:(0,o.t)("Index column"),tip:(0,o.t)("Column to use as the index of the dataframe. If None is given, Index label is used."),name:"index_column",children:(0,n.Y)(_.A,{ariaLabel:(0,o.t)("Choose index column"),options:z.map((e=>({value:e,label:e}))),allowClear:!0,allowNewOptions:!0})})})}),ne&&(0,n.Y)(u.A,{children:(0,n.Y)(p.A,{span:24,children:(0,n.Y)(U,{label:(0,o.t)("Index label"),tip:(0,o.t)("Label for the index column. Don't use an existing column name."),name:"index_label",children:(0,n.Y)(v.A,{"aria-label":(0,o.t)("Index label"),type:"text"})})})})]})},...j("header_row",C)&&j("rows_to_read",C)&&j("skip_rows",C)?[{key:"rows",label:(0,n.Y)(h.o.Text,{strong:!0,children:(0,o.t)("Rows")}),children:(0,n.FD)(u.A,{children:[(0,n.Y)(p.A,{span:8,children:(0,n.Y)(U,{label:(0,o.t)("Header row"),tip:(0,o.t)("Row containing the headers to use as column names (0 is first line of data)."),name:"header_row",rules:[{required:!0,message:"Header row is required"}],children:(0,n.Y)(f.A,{"aria-label":(0,o.t)("Header row"),type:"text",min:0})})}),(0,n.Y)(p.A,{span:8,children:(0,n.Y)(U,{label:(0,o.t)("Rows to read"),tip:(0,o.t)("Number of rows of file to read. Leave empty (default) to read all rows"),name:"rows_to_read",children:(0,n.Y)(f.A,{"aria-label":(0,o.t)("Rows to read"),min:1})})}),(0,n.Y)(p.A,{span:8,children:(0,n.Y)(U,{label:(0,o.t)("Skip rows"),tip:(0,o.t)("Number of rows to skip at start of file."),name:"skip_rows",rules:[{required:!0,message:"Skip rows is required"}],children:(0,n.Y)(f.A,{"aria-label":(0,o.t)("Skip rows"),min:0})})})]})}]:[]]})})})}))},24777:(e,a,t)=>{var n;function l(e,a){try{const t=localStorage.getItem(e);return null===t?a:JSON.parse(t)}catch{return a}}function i(e,a){try{localStorage.setItem(e,JSON.stringify(a))}catch{}}function r(e,a){return l(e,a)}function o(e,a){i(e,a)}t.d(a,{Gq:()=>r,Hh:()=>n,SO:()=>o,SX:()=>l,Wr:()=>i}),function(e){e.Database="db",e.ChartSplitSizes="chart_split_sizes",e.ControlsWidth="controls_width",e.DatasourceWidth="datasource_width",e.IsDatapanelOpen="is_datapanel_open",e.HomepageChartFilter="homepage_chart_filter",e.HomepageDashboardFilter="homepage_dashboard_filter",e.HomepageCollapseState="homepage_collapse_state",e.HomepageActivityFilter="homepage_activity_filter",e.DatasetnameSetSuccessful="datasetname_set_successful",e.SqllabIsAutocompleteEnabled="sqllab__is_autocomplete_enabled",e.SqllabIsRenderHtmlEnabled="sqllab__is_render_html_enabled",e.ExploreDataTableOriginalFormattedTimeColumns="explore__data_table_original_formatted_time_columns",e.DashboardCustomFilterBarWidths="dashboard__custom_filter_bar_widths",e.DashboardExploreContext="dashboard__explore_context",e.DashboardEditorShowOnlyMyCharts="dashboard__editor_show_only_my_charts",e.CommonResizableSidebarWidths="common__resizable_sidebar_widths"}(n||(n={}))}}]);