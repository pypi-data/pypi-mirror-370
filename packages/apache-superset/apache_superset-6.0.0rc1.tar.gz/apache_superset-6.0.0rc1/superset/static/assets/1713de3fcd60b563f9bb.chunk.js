(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[7094],{19049:(e,t,r)=>{var i=r(79920)("capitalize",r(14792),r(96493));i.placeholder=r(2874),e.exports=i},68793:(e,t,r)=>{"use strict";r.r(t),r.d(t,{default:()=>w});var i,n=r(19049),l=r.n(n),o=r(2445),a=r(50290),c=r(17437),s=r(79378),u=r(74098),h=r(4651),d=r(42566),m=r(65729),p=r(8558),f=r(76576),g=r(88217),A=r(17355),y=r(96540),Y=r(32064);!function(e){e[e.AuthOID=0]="AuthOID",e[e.AuthDB=1]="AuthDB",e[e.AuthLDAP=2]="AuthLDAP",e[e.AuthOauth=4]="AuthOauth"}(i||(i={}));const b=(0,a.I4)(h.Z)`
  ${({theme:e})=>c.AH`
    max-width: 400px;
    width: 100%;
    margin-top: ${e.marginXL}px;
    color: ${e.colorBgContainer};
    background: ${e.colorBgBase};
    .ant-form-item-label label {
      color: ${e.colorPrimary};
    }
  `}
`,D=(0,a.I4)(d.o.Text)`
  ${({theme:e})=>c.AH`
    font-size: ${e.fontSizeSM}px;
  `}
`;function w(){const[e]=m.l.useForm(),[t,r]=(0,y.useState)(!1),n=(0,Y.Ay)(),a=n.common.conf.AUTH_TYPE,h=n.common.conf.AUTH_PROVIDERS,w=n.common.conf.AUTH_USER_REGISTRATION,$=e=>{if(!e||"string"!=typeof e)return;const t=`${l()(e)}Outlined`,r=p.F[t];return r&&"function"==typeof r?(0,o.Y)(r,{}):void 0};return(0,o.Y)(f.s,{justify:"center",align:"center",css:c.AH`
        width: 100%;
        height: calc(100vh - 200px);
      `,children:(0,o.FD)(b,{title:(0,u.t)("Sign in"),padded:!0,children:[a===i.AuthOID&&(0,o.Y)(f.s,{justify:"center",vertical:!0,gap:"middle",children:(0,o.Y)(m.l,{layout:"vertical",requiredMark:"optional",form:e,children:h.map((e=>(0,o.Y)(m.l.Item,{children:(0,o.FD)(g.$,{href:`/login/${e.name}`,block:!0,iconPosition:"start",icon:$(e.name),children:[(0,u.t)("Sign in with")," ",l()(e.name)]})})))})}),a===i.AuthOauth&&(0,o.Y)(f.s,{justify:"center",gap:0,vertical:!0,children:(0,o.Y)(m.l,{layout:"vertical",requiredMark:"optional",form:e,children:h.map((e=>(0,o.Y)(m.l.Item,{children:(0,o.FD)(g.$,{href:`/login/${e.name}`,block:!0,iconPosition:"start",icon:$(e.name),children:[(0,u.t)("Sign in with")," ",l()(e.name)]})})))})}),(a===i.AuthDB||a===i.AuthLDAP)&&(0,o.FD)(f.s,{justify:"center",vertical:!0,gap:"middle",children:[(0,o.Y)(d.o.Text,{type:"secondary",children:(0,u.t)("Enter your login and password below:")}),(0,o.FD)(m.l,{layout:"vertical",requiredMark:"optional",form:e,onFinish:e=>{r(!0),s.A.postForm("/login/",e,"").finally((()=>{r(!1)}))},children:[(0,o.Y)(m.l.Item,{label:(0,o.Y)(D,{children:(0,u.t)("Username:")}),name:"username",rules:[{required:!0,message:(0,u.t)("Please enter your username")}],children:(0,o.Y)(A.A,{autoFocus:!0,prefix:(0,o.Y)(p.F.UserOutlined,{iconSize:"l"})})}),(0,o.Y)(m.l.Item,{label:(0,o.Y)(D,{children:(0,u.t)("Password:")}),name:"password",rules:[{required:!0,message:(0,u.t)("Please enter your password")}],children:(0,o.Y)(A.A.Password,{prefix:(0,o.Y)(p.F.KeyOutlined,{iconSize:"l"})})}),(0,o.Y)(m.l.Item,{label:null,children:(0,o.FD)(f.s,{css:c.AH`
                    width: 100%;
                  `,children:[(0,o.Y)(g.$,{block:!0,type:"primary",htmlType:"submit",loading:t,children:(0,u.t)("Sign in")}),w&&(0,o.Y)(g.$,{block:!0,type:"default",href:"/register/",children:(0,u.t)("Register")})]})})]})]})]})})}},96493:e=>{e.exports={cap:!1,curry:!1,fixed:!1,immutable:!1,rearg:!1}}}]);