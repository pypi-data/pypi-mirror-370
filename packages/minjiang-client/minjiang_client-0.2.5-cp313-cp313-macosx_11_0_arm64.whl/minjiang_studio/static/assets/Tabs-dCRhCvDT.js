import{d as J,I as l,r as $,dC as bt,dD as he,dE as ct,cC as ft,bJ as pt,at as Ce,dr as ut,bp as vt,ch as ht,a1 as gt,aq as xt,dF as mt,C as q,d7 as yt,ab as r,ad as n,ae as u,af as y,ac as wt,aQ as te,bR as ge,dG as ae,ag as Ct,am as Se,dH as St,dI as xe,av as Rt,aH as re,aW as oe,o as zt,aj as $t,aw as E,dJ as Tt,co as Pt,ao as j,cl as K,ap as _t,aV as Wt,bP as Lt,dK as At,b7 as Bt,dL as Et,aB as Y}from"./index-DOdIYOkR.js";import{A as jt}from"./Add-Cl6tY5vX.js";import{d as kt}from"./debounce-HnRb9GPW.js";const Ht=he(".v-x-scroll",{overflow:"auto",scrollbarWidth:"none"},[he("&::-webkit-scrollbar",{width:0,height:0})]),Ot=J({name:"XScroll",props:{disabled:Boolean,onScroll:Function},setup(){const e=$(null);function i(d){!(d.currentTarget.offsetWidth<d.currentTarget.scrollWidth)||d.deltaY===0||(d.currentTarget.scrollLeft+=d.deltaY+d.deltaX,d.preventDefault())}const b=bt();return Ht.mount({id:"vueuc/x-scroll",head:!0,anchorMetaName:ct,ssr:b}),Object.assign({selfRef:e,handleWheel:i},{scrollTo(...d){var w;(w=e.value)===null||w===void 0||w.scrollTo(...d)}})},render(){return l("div",{ref:"selfRef",onScroll:this.onScroll,onWheel:this.disabled?void 0:this.handleWheel,class:"v-x-scroll"},this.$slots)}});var Ft="Expected a function";function ne(e,i,b){var v=!0,d=!0;if(typeof e!="function")throw new TypeError(Ft);return ft(b)&&(v="leading"in b?!!b.leading:v,d="trailing"in b?!!b.trailing:d),kt(e,i,{leading:v,maxWait:i,trailing:d})}const le=pt("n-tabs"),Re={tab:[String,Number,Object,Function],name:{type:[String,Number],required:!0},disabled:Boolean,displayDirective:{type:String,default:"if"},closable:{type:Boolean,default:void 0},tabProps:Object,label:[String,Number,Object,Function]},Ut=J({__TAB_PANE__:!0,name:"TabPane",alias:["TabPanel"],props:Re,slots:Object,setup(e){const i=Ce(le,null);return i||ut("tab-pane","`n-tab-pane` must be placed inside `n-tabs`."),{style:i.paneStyleRef,class:i.paneClassRef,mergedClsPrefix:i.mergedClsPrefixRef}},render(){return l("div",{class:[`${this.mergedClsPrefix}-tab-pane`,this.class],style:this.style},this.$slots)}}),It=Object.assign({internalLeftPadded:Boolean,internalAddable:Boolean,internalCreatedByPane:Boolean},yt(Re,["displayDirective"])),se=J({__TAB__:!0,inheritAttrs:!1,name:"Tab",props:It,setup(e){const{mergedClsPrefixRef:i,valueRef:b,typeRef:v,closableRef:d,tabStyleRef:w,addTabStyleRef:h,tabClassRef:C,addTabClassRef:S,tabChangeIdRef:g,onBeforeLeaveRef:f,triggerRef:k,handleAdd:A,activateTab:x,handleClose:R}=Ce(le);return{trigger:k,mergedClosable:q(()=>{if(e.internalAddable)return!1;const{closable:m}=e;return m===void 0?d.value:m}),style:w,addStyle:h,tabClass:C,addTabClass:S,clsPrefix:i,value:b,type:v,handleClose(m){m.stopPropagation(),!e.disabled&&R(e.name)},activateTab(){if(e.disabled)return;if(e.internalAddable){A();return}const{name:m}=e,P=++g.id;if(m!==b.value){const{value:B}=f;B?Promise.resolve(B(e.name,b.value)).then(T=>{T&&g.id===P&&x(m)}):x(m)}}}},render(){const{internalAddable:e,clsPrefix:i,name:b,disabled:v,label:d,tab:w,value:h,mergedClosable:C,trigger:S,$slots:{default:g}}=this,f=d??w;return l("div",{class:`${i}-tabs-tab-wrapper`},this.internalLeftPadded?l("div",{class:`${i}-tabs-tab-pad`}):null,l("div",Object.assign({key:b,"data-name":b,"data-disabled":v?!0:void 0},vt({class:[`${i}-tabs-tab`,h===b&&`${i}-tabs-tab--active`,v&&`${i}-tabs-tab--disabled`,C&&`${i}-tabs-tab--closable`,e&&`${i}-tabs-tab--addable`,e?this.addTabClass:this.tabClass],onClick:S==="click"?this.activateTab:void 0,onMouseenter:S==="hover"?this.activateTab:void 0,style:e?this.addStyle:this.style},this.internalCreatedByPane?this.tabProps||{}:this.$attrs)),l("span",{class:`${i}-tabs-tab__label`},e?l(gt,null,l("div",{class:`${i}-tabs-tab__height-placeholder`}," "),l(xt,{clsPrefix:i},{default:()=>l(jt,null)})):g?g():typeof f=="object"?f:ht(f??b)),C&&this.type==="card"?l(mt,{clsPrefix:i,class:`${i}-tabs-tab__close`,onClick:this.handleClose,disabled:v}):null))}}),Dt=r("tabs",`
 box-sizing: border-box;
 width: 100%;
 display: flex;
 flex-direction: column;
 transition:
 background-color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
`,[n("segment-type",[r("tabs-rail",[u("&.transition-disabled",[r("tabs-capsule",`
 transition: none;
 `)])])]),n("top",[r("tab-pane",`
 padding: var(--n-pane-padding-top) var(--n-pane-padding-right) var(--n-pane-padding-bottom) var(--n-pane-padding-left);
 `)]),n("left",[r("tab-pane",`
 padding: var(--n-pane-padding-right) var(--n-pane-padding-bottom) var(--n-pane-padding-left) var(--n-pane-padding-top);
 `)]),n("left, right",`
 flex-direction: row;
 `,[r("tabs-bar",`
 width: 2px;
 right: 0;
 transition:
 top .2s var(--n-bezier),
 max-height .2s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `),r("tabs-tab",`
 padding: var(--n-tab-padding-vertical); 
 `)]),n("right",`
 flex-direction: row-reverse;
 `,[r("tab-pane",`
 padding: var(--n-pane-padding-left) var(--n-pane-padding-top) var(--n-pane-padding-right) var(--n-pane-padding-bottom);
 `),r("tabs-bar",`
 left: 0;
 `)]),n("bottom",`
 flex-direction: column-reverse;
 justify-content: flex-end;
 `,[r("tab-pane",`
 padding: var(--n-pane-padding-bottom) var(--n-pane-padding-right) var(--n-pane-padding-top) var(--n-pane-padding-left);
 `),r("tabs-bar",`
 top: 0;
 `)]),r("tabs-rail",`
 position: relative;
 padding: 3px;
 border-radius: var(--n-tab-border-radius);
 width: 100%;
 background-color: var(--n-color-segment);
 transition: background-color .3s var(--n-bezier);
 display: flex;
 align-items: center;
 `,[r("tabs-capsule",`
 border-radius: var(--n-tab-border-radius);
 position: absolute;
 pointer-events: none;
 background-color: var(--n-tab-color-segment);
 box-shadow: 0 1px 3px 0 rgba(0, 0, 0, .08);
 transition: transform 0.3s var(--n-bezier);
 `),r("tabs-tab-wrapper",`
 flex-basis: 0;
 flex-grow: 1;
 display: flex;
 align-items: center;
 justify-content: center;
 `,[r("tabs-tab",`
 overflow: hidden;
 border-radius: var(--n-tab-border-radius);
 width: 100%;
 display: flex;
 align-items: center;
 justify-content: center;
 `,[n("active",`
 font-weight: var(--n-font-weight-strong);
 color: var(--n-tab-text-color-active);
 `),u("&:hover",`
 color: var(--n-tab-text-color-hover);
 `)])])]),n("flex",[r("tabs-nav",`
 width: 100%;
 position: relative;
 `,[r("tabs-wrapper",`
 width: 100%;
 `,[r("tabs-tab",`
 margin-right: 0;
 `)])])]),r("tabs-nav",`
 box-sizing: border-box;
 line-height: 1.5;
 display: flex;
 transition: border-color .3s var(--n-bezier);
 `,[y("prefix, suffix",`
 display: flex;
 align-items: center;
 `),y("prefix","padding-right: 16px;"),y("suffix","padding-left: 16px;")]),n("top, bottom",[r("tabs-nav-scroll-wrapper",[u("&::before",`
 top: 0;
 bottom: 0;
 left: 0;
 width: 20px;
 `),u("&::after",`
 top: 0;
 bottom: 0;
 right: 0;
 width: 20px;
 `),n("shadow-start",[u("&::before",`
 box-shadow: inset 10px 0 8px -8px rgba(0, 0, 0, .12);
 `)]),n("shadow-end",[u("&::after",`
 box-shadow: inset -10px 0 8px -8px rgba(0, 0, 0, .12);
 `)])])]),n("left, right",[r("tabs-nav-scroll-content",`
 flex-direction: column;
 `),r("tabs-nav-scroll-wrapper",[u("&::before",`
 top: 0;
 left: 0;
 right: 0;
 height: 20px;
 `),u("&::after",`
 bottom: 0;
 left: 0;
 right: 0;
 height: 20px;
 `),n("shadow-start",[u("&::before",`
 box-shadow: inset 0 10px 8px -8px rgba(0, 0, 0, .12);
 `)]),n("shadow-end",[u("&::after",`
 box-shadow: inset 0 -10px 8px -8px rgba(0, 0, 0, .12);
 `)])])]),r("tabs-nav-scroll-wrapper",`
 flex: 1;
 position: relative;
 overflow: hidden;
 `,[r("tabs-nav-y-scroll",`
 height: 100%;
 width: 100%;
 overflow-y: auto; 
 scrollbar-width: none;
 `,[u("&::-webkit-scrollbar, &::-webkit-scrollbar-track-piece, &::-webkit-scrollbar-thumb",`
 width: 0;
 height: 0;
 display: none;
 `)]),u("&::before, &::after",`
 transition: box-shadow .3s var(--n-bezier);
 pointer-events: none;
 content: "";
 position: absolute;
 z-index: 1;
 `)]),r("tabs-nav-scroll-content",`
 display: flex;
 position: relative;
 min-width: 100%;
 min-height: 100%;
 width: fit-content;
 box-sizing: border-box;
 `),r("tabs-wrapper",`
 display: inline-flex;
 flex-wrap: nowrap;
 position: relative;
 `),r("tabs-tab-wrapper",`
 display: flex;
 flex-wrap: nowrap;
 flex-shrink: 0;
 flex-grow: 0;
 `),r("tabs-tab",`
 cursor: pointer;
 white-space: nowrap;
 flex-wrap: nowrap;
 display: inline-flex;
 align-items: center;
 color: var(--n-tab-text-color);
 font-size: var(--n-tab-font-size);
 background-clip: padding-box;
 padding: var(--n-tab-padding);
 transition:
 box-shadow .3s var(--n-bezier),
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 `,[n("disabled",{cursor:"not-allowed"}),y("close",`
 margin-left: 6px;
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 `),y("label",`
 display: flex;
 align-items: center;
 z-index: 1;
 `)]),r("tabs-bar",`
 position: absolute;
 bottom: 0;
 height: 2px;
 border-radius: 1px;
 background-color: var(--n-bar-color);
 transition:
 left .2s var(--n-bezier),
 max-width .2s var(--n-bezier),
 opacity .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `,[u("&.transition-disabled",`
 transition: none;
 `),n("disabled",`
 background-color: var(--n-tab-text-color-disabled)
 `)]),r("tabs-pane-wrapper",`
 position: relative;
 overflow: hidden;
 transition: max-height .2s var(--n-bezier);
 `),r("tab-pane",`
 color: var(--n-pane-text-color);
 width: 100%;
 transition:
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 opacity .2s var(--n-bezier);
 left: 0;
 right: 0;
 top: 0;
 `,[u("&.next-transition-leave-active, &.prev-transition-leave-active, &.next-transition-enter-active, &.prev-transition-enter-active",`
 transition:
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 transform .2s var(--n-bezier),
 opacity .2s var(--n-bezier);
 `),u("&.next-transition-leave-active, &.prev-transition-leave-active",`
 position: absolute;
 `),u("&.next-transition-enter-from, &.prev-transition-leave-to",`
 transform: translateX(32px);
 opacity: 0;
 `),u("&.next-transition-leave-to, &.prev-transition-enter-from",`
 transform: translateX(-32px);
 opacity: 0;
 `),u("&.next-transition-leave-from, &.next-transition-enter-to, &.prev-transition-leave-from, &.prev-transition-enter-to",`
 transform: translateX(0);
 opacity: 1;
 `)]),r("tabs-tab-pad",`
 box-sizing: border-box;
 width: var(--n-tab-gap);
 flex-grow: 0;
 flex-shrink: 0;
 `),n("line-type, bar-type",[r("tabs-tab",`
 font-weight: var(--n-tab-font-weight);
 box-sizing: border-box;
 vertical-align: bottom;
 `,[u("&:hover",{color:"var(--n-tab-text-color-hover)"}),n("active",`
 color: var(--n-tab-text-color-active);
 font-weight: var(--n-tab-font-weight-active);
 `),n("disabled",{color:"var(--n-tab-text-color-disabled)"})])]),r("tabs-nav",[n("line-type",[n("top",[y("prefix, suffix",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),r("tabs-nav-scroll-content",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),r("tabs-bar",`
 bottom: -1px;
 `)]),n("left",[y("prefix, suffix",`
 border-right: 1px solid var(--n-tab-border-color);
 `),r("tabs-nav-scroll-content",`
 border-right: 1px solid var(--n-tab-border-color);
 `),r("tabs-bar",`
 right: -1px;
 `)]),n("right",[y("prefix, suffix",`
 border-left: 1px solid var(--n-tab-border-color);
 `),r("tabs-nav-scroll-content",`
 border-left: 1px solid var(--n-tab-border-color);
 `),r("tabs-bar",`
 left: -1px;
 `)]),n("bottom",[y("prefix, suffix",`
 border-top: 1px solid var(--n-tab-border-color);
 `),r("tabs-nav-scroll-content",`
 border-top: 1px solid var(--n-tab-border-color);
 `),r("tabs-bar",`
 top: -1px;
 `)]),y("prefix, suffix",`
 transition: border-color .3s var(--n-bezier);
 `),r("tabs-nav-scroll-content",`
 transition: border-color .3s var(--n-bezier);
 `),r("tabs-bar",`
 border-radius: 0;
 `)]),n("card-type",[y("prefix, suffix",`
 transition: border-color .3s var(--n-bezier);
 `),r("tabs-pad",`
 flex-grow: 1;
 transition: border-color .3s var(--n-bezier);
 `),r("tabs-tab-pad",`
 transition: border-color .3s var(--n-bezier);
 `),r("tabs-tab",`
 font-weight: var(--n-tab-font-weight);
 border: 1px solid var(--n-tab-border-color);
 background-color: var(--n-tab-color);
 box-sizing: border-box;
 position: relative;
 vertical-align: bottom;
 display: flex;
 justify-content: space-between;
 font-size: var(--n-tab-font-size);
 color: var(--n-tab-text-color);
 `,[n("addable",`
 padding-left: 8px;
 padding-right: 8px;
 font-size: 16px;
 justify-content: center;
 `,[y("height-placeholder",`
 width: 0;
 font-size: var(--n-tab-font-size);
 `),wt("disabled",[u("&:hover",`
 color: var(--n-tab-text-color-hover);
 `)])]),n("closable","padding-right: 8px;"),n("active",`
 background-color: #0000;
 font-weight: var(--n-tab-font-weight-active);
 color: var(--n-tab-text-color-active);
 `),n("disabled","color: var(--n-tab-text-color-disabled);")])]),n("left, right",`
 flex-direction: column; 
 `,[y("prefix, suffix",`
 padding: var(--n-tab-padding-vertical);
 `),r("tabs-wrapper",`
 flex-direction: column;
 `),r("tabs-tab-wrapper",`
 flex-direction: column;
 `,[r("tabs-tab-pad",`
 height: var(--n-tab-gap-vertical);
 width: 100%;
 `)])]),n("top",[n("card-type",[r("tabs-scroll-padding","border-bottom: 1px solid var(--n-tab-border-color);"),y("prefix, suffix",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),r("tabs-tab",`
 border-top-left-radius: var(--n-tab-border-radius);
 border-top-right-radius: var(--n-tab-border-radius);
 `,[n("active",`
 border-bottom: 1px solid #0000;
 `)]),r("tabs-tab-pad",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),r("tabs-pad",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `)])]),n("left",[n("card-type",[r("tabs-scroll-padding","border-right: 1px solid var(--n-tab-border-color);"),y("prefix, suffix",`
 border-right: 1px solid var(--n-tab-border-color);
 `),r("tabs-tab",`
 border-top-left-radius: var(--n-tab-border-radius);
 border-bottom-left-radius: var(--n-tab-border-radius);
 `,[n("active",`
 border-right: 1px solid #0000;
 `)]),r("tabs-tab-pad",`
 border-right: 1px solid var(--n-tab-border-color);
 `),r("tabs-pad",`
 border-right: 1px solid var(--n-tab-border-color);
 `)])]),n("right",[n("card-type",[r("tabs-scroll-padding","border-left: 1px solid var(--n-tab-border-color);"),y("prefix, suffix",`
 border-left: 1px solid var(--n-tab-border-color);
 `),r("tabs-tab",`
 border-top-right-radius: var(--n-tab-border-radius);
 border-bottom-right-radius: var(--n-tab-border-radius);
 `,[n("active",`
 border-left: 1px solid #0000;
 `)]),r("tabs-tab-pad",`
 border-left: 1px solid var(--n-tab-border-color);
 `),r("tabs-pad",`
 border-left: 1px solid var(--n-tab-border-color);
 `)])]),n("bottom",[n("card-type",[r("tabs-scroll-padding","border-top: 1px solid var(--n-tab-border-color);"),y("prefix, suffix",`
 border-top: 1px solid var(--n-tab-border-color);
 `),r("tabs-tab",`
 border-bottom-left-radius: var(--n-tab-border-radius);
 border-bottom-right-radius: var(--n-tab-border-radius);
 `,[n("active",`
 border-top: 1px solid #0000;
 `)]),r("tabs-tab-pad",`
 border-top: 1px solid var(--n-tab-border-color);
 `),r("tabs-pad",`
 border-top: 1px solid var(--n-tab-border-color);
 `)])])])]),Mt=Object.assign(Object.assign({},Se.props),{value:[String,Number],defaultValue:[String,Number],trigger:{type:String,default:"click"},type:{type:String,default:"bar"},closable:Boolean,justifyContent:String,size:{type:String,default:"medium"},placement:{type:String,default:"top"},tabStyle:[String,Object],tabClass:String,addTabStyle:[String,Object],addTabClass:String,barWidth:Number,paneClass:String,paneStyle:[String,Object],paneWrapperClass:String,paneWrapperStyle:[String,Object],addable:[Boolean,Object],tabsPadding:{type:Number,default:0},animated:Boolean,onBeforeLeave:Function,onAdd:Function,"onUpdate:value":[Function,Array],onUpdateValue:[Function,Array],onClose:[Function,Array],labelSize:String,activeName:[String,Number],onActiveNameChange:[Function,Array]}),Gt=J({name:"Tabs",props:Mt,slots:Object,setup(e,{slots:i}){var b,v,d,w;const{mergedClsPrefixRef:h,inlineThemeDisabled:C}=Ct(e),S=Se("Tabs","-tabs",Dt,St,e,h),g=$(null),f=$(null),k=$(null),A=$(null),x=$(null),R=$(null),m=$(!0),P=$(!0),B=xe(e,["labelSize","size"]),T=xe(e,["activeName","value"]),V=$((v=(b=T.value)!==null&&b!==void 0?b:e.defaultValue)!==null&&v!==void 0?v:i.default?(w=(d=te(i.default())[0])===null||d===void 0?void 0:d.props)===null||w===void 0?void 0:w.name:null),_=Rt(T,V),c={id:0},z=q(()=>{if(!(!e.justifyContent||e.type==="card"))return{display:"flex",justifyContent:e.justifyContent}});re(_,()=>{c.id=0,X(),be()});function H(){var t;const{value:a}=_;return a===null?null:(t=g.value)===null||t===void 0?void 0:t.querySelector(`[data-name="${a}"]`)}function ze(t){if(e.type==="card")return;const{value:a}=f;if(!a)return;const o=a.style.opacity==="0";if(t){const s=`${h.value}-tabs-bar--disabled`,{barWidth:p,placement:W}=e;if(t.dataset.disabled==="true"?a.classList.add(s):a.classList.remove(s),["top","bottom"].includes(W)){if(de(["top","maxHeight","height"]),typeof p=="number"&&t.offsetWidth>=p){const L=Math.floor((t.offsetWidth-p)/2)+t.offsetLeft;a.style.left=`${L}px`,a.style.maxWidth=`${p}px`}else a.style.left=`${t.offsetLeft}px`,a.style.maxWidth=`${t.offsetWidth}px`;a.style.width="8192px",o&&(a.style.transition="none"),a.offsetWidth,o&&(a.style.transition="",a.style.opacity="1")}else{if(de(["left","maxWidth","width"]),typeof p=="number"&&t.offsetHeight>=p){const L=Math.floor((t.offsetHeight-p)/2)+t.offsetTop;a.style.top=`${L}px`,a.style.maxHeight=`${p}px`}else a.style.top=`${t.offsetTop}px`,a.style.maxHeight=`${t.offsetHeight}px`;a.style.height="8192px",o&&(a.style.transition="none"),a.offsetHeight,o&&(a.style.transition="",a.style.opacity="1")}}}function $e(){if(e.type==="card")return;const{value:t}=f;t&&(t.style.opacity="0")}function de(t){const{value:a}=f;if(a)for(const o of t)a.style[o]=""}function X(){if(e.type==="card")return;const t=H();t?ze(t):$e()}function be(){var t;const a=(t=x.value)===null||t===void 0?void 0:t.$el;if(!a)return;const o=H();if(!o)return;const{scrollLeft:s,offsetWidth:p}=a,{offsetLeft:W,offsetWidth:L}=o;s>W?a.scrollTo({top:0,left:W,behavior:"smooth"}):W+L>s+p&&a.scrollTo({top:0,left:W+L-p,behavior:"smooth"})}const U=$(null);let Q=0,O=null;function Te(t){const a=U.value;if(a){Q=t.getBoundingClientRect().height;const o=`${Q}px`,s=()=>{a.style.height=o,a.style.maxHeight=o};O?(s(),O(),O=null):O=s}}function Pe(t){const a=U.value;if(a){const o=t.getBoundingClientRect().height,s=()=>{document.body.offsetHeight,a.style.maxHeight=`${o}px`,a.style.height=`${Math.max(Q,o)}px`};O?(O(),O=null,s()):O=s}}function _e(){const t=U.value;if(t){t.style.maxHeight="",t.style.height="";const{paneWrapperStyle:a}=e;if(typeof a=="string")t.style.cssText=a;else if(a){const{maxHeight:o,height:s}=a;o!==void 0&&(t.style.maxHeight=o),s!==void 0&&(t.style.height=s)}}}const ce={value:[]},fe=$("next");function We(t){const a=_.value;let o="next";for(const s of ce.value){if(s===a)break;if(s===t){o="prev";break}}fe.value=o,Le(t)}function Le(t){const{onActiveNameChange:a,onUpdateValue:o,"onUpdate:value":s}=e;a&&Y(a,t),o&&Y(o,t),s&&Y(s,t),V.value=t}function Ae(t){const{onClose:a}=e;a&&Y(a,t)}function pe(){const{value:t}=f;if(!t)return;const a="transition-disabled";t.classList.add(a),X(),t.classList.remove(a)}const F=$(null);function Z({transitionDisabled:t}){const a=g.value;if(!a)return;t&&a.classList.add("transition-disabled");const o=H();o&&F.value&&(F.value.style.width=`${o.offsetWidth}px`,F.value.style.height=`${o.offsetHeight}px`,F.value.style.transform=`translateX(${o.offsetLeft-Wt(getComputedStyle(a).paddingLeft)}px)`,t&&F.value.offsetWidth),t&&a.classList.remove("transition-disabled")}re([_],()=>{e.type==="segment"&&oe(()=>{Z({transitionDisabled:!1})})}),zt(()=>{e.type==="segment"&&Z({transitionDisabled:!0})});let ue=0;function Be(t){var a;if(t.contentRect.width===0&&t.contentRect.height===0||ue===t.contentRect.width)return;ue=t.contentRect.width;const{type:o}=e;if((o==="line"||o==="bar")&&pe(),o!=="segment"){const{placement:s}=e;ee((s==="top"||s==="bottom"?(a=x.value)===null||a===void 0?void 0:a.$el:R.value)||null)}}const Ee=ne(Be,64);re([()=>e.justifyContent,()=>e.size],()=>{oe(()=>{const{type:t}=e;(t==="line"||t==="bar")&&pe()})});const I=$(!1);function je(t){var a;const{target:o,contentRect:{width:s,height:p}}=t,W=o.parentElement.parentElement.offsetWidth,L=o.parentElement.parentElement.offsetHeight,{placement:M}=e;if(!I.value)M==="top"||M==="bottom"?W<s&&(I.value=!0):L<p&&(I.value=!0);else{const{value:N}=A;if(!N)return;M==="top"||M==="bottom"?W-s>N.$el.offsetWidth&&(I.value=!1):L-p>N.$el.offsetHeight&&(I.value=!1)}ee(((a=x.value)===null||a===void 0?void 0:a.$el)||null)}const ke=ne(je,64);function He(){const{onAdd:t}=e;t&&t(),oe(()=>{const a=H(),{value:o}=x;!a||!o||o.scrollTo({left:a.offsetLeft,top:0,behavior:"smooth"})})}function ee(t){if(!t)return;const{placement:a}=e;if(a==="top"||a==="bottom"){const{scrollLeft:o,scrollWidth:s,offsetWidth:p}=t;m.value=o<=0,P.value=o+p>=s}else{const{scrollTop:o,scrollHeight:s,offsetHeight:p}=t;m.value=o<=0,P.value=o+p>=s}}const Oe=ne(t=>{ee(t.target)},64);$t(le,{triggerRef:E(e,"trigger"),tabStyleRef:E(e,"tabStyle"),tabClassRef:E(e,"tabClass"),addTabStyleRef:E(e,"addTabStyle"),addTabClassRef:E(e,"addTabClass"),paneClassRef:E(e,"paneClass"),paneStyleRef:E(e,"paneStyle"),mergedClsPrefixRef:h,typeRef:E(e,"type"),closableRef:E(e,"closable"),valueRef:_,tabChangeIdRef:c,onBeforeLeaveRef:E(e,"onBeforeLeave"),activateTab:We,handleClose:Ae,handleAdd:He}),Tt(()=>{X(),be()}),Pt(()=>{const{value:t}=k;if(!t)return;const{value:a}=h,o=`${a}-tabs-nav-scroll-wrapper--shadow-start`,s=`${a}-tabs-nav-scroll-wrapper--shadow-end`;m.value?t.classList.remove(o):t.classList.add(o),P.value?t.classList.remove(s):t.classList.add(s)});const Fe={syncBarPosition:()=>{X()}},Ie=()=>{Z({transitionDisabled:!0})},ve=q(()=>{const{value:t}=B,{type:a}=e,o={card:"Card",bar:"Bar",line:"Line",segment:"Segment"}[a],s=`${t}${o}`,{self:{barColor:p,closeIconColor:W,closeIconColorHover:L,closeIconColorPressed:M,tabColor:N,tabBorderColor:De,paneTextColor:Me,tabFontWeight:Ve,tabBorderRadius:Ne,tabFontWeightActive:Xe,colorSegment:Ue,fontWeightStrong:Ge,tabColorSegment:Ke,closeSize:Ye,closeIconSize:qe,closeColorHover:Je,closeColorPressed:Qe,closeBorderRadius:Ze,[j("panePadding",t)]:G,[j("tabPadding",s)]:et,[j("tabPaddingVertical",s)]:tt,[j("tabGap",s)]:at,[j("tabGap",`${s}Vertical`)]:rt,[j("tabTextColor",a)]:ot,[j("tabTextColorActive",a)]:nt,[j("tabTextColorHover",a)]:it,[j("tabTextColorDisabled",a)]:st,[j("tabFontSize",t)]:lt},common:{cubicBezierEaseInOut:dt}}=S.value;return{"--n-bezier":dt,"--n-color-segment":Ue,"--n-bar-color":p,"--n-tab-font-size":lt,"--n-tab-text-color":ot,"--n-tab-text-color-active":nt,"--n-tab-text-color-disabled":st,"--n-tab-text-color-hover":it,"--n-pane-text-color":Me,"--n-tab-border-color":De,"--n-tab-border-radius":Ne,"--n-close-size":Ye,"--n-close-icon-size":qe,"--n-close-color-hover":Je,"--n-close-color-pressed":Qe,"--n-close-border-radius":Ze,"--n-close-icon-color":W,"--n-close-icon-color-hover":L,"--n-close-icon-color-pressed":M,"--n-tab-color":N,"--n-tab-font-weight":Ve,"--n-tab-font-weight-active":Xe,"--n-tab-padding":et,"--n-tab-padding-vertical":tt,"--n-tab-gap":at,"--n-tab-gap-vertical":rt,"--n-pane-padding-left":K(G,"left"),"--n-pane-padding-right":K(G,"right"),"--n-pane-padding-top":K(G,"top"),"--n-pane-padding-bottom":K(G,"bottom"),"--n-font-weight-strong":Ge,"--n-tab-color-segment":Ke}}),D=C?_t("tabs",q(()=>`${B.value[0]}${e.type[0]}`),ve,e):void 0;return Object.assign({mergedClsPrefix:h,mergedValue:_,renderedNames:new Set,segmentCapsuleElRef:F,tabsPaneWrapperRef:U,tabsElRef:g,barElRef:f,addTabInstRef:A,xScrollInstRef:x,scrollWrapperElRef:k,addTabFixed:I,tabWrapperStyle:z,handleNavResize:Ee,mergedSize:B,handleScroll:Oe,handleTabsResize:ke,cssVars:C?void 0:ve,themeClass:D==null?void 0:D.themeClass,animationDirection:fe,renderNameListRef:ce,yScrollElRef:R,handleSegmentResize:Ie,onAnimationBeforeLeave:Te,onAnimationEnter:Pe,onAnimationAfterEnter:_e,onRender:D==null?void 0:D.onRender},Fe)},render(){const{mergedClsPrefix:e,type:i,placement:b,addTabFixed:v,addable:d,mergedSize:w,renderNameListRef:h,onRender:C,paneWrapperClass:S,paneWrapperStyle:g,$slots:{default:f,prefix:k,suffix:A}}=this;C==null||C();const x=f?te(f()).filter(c=>c.type.__TAB_PANE__===!0):[],R=f?te(f()).filter(c=>c.type.__TAB__===!0):[],m=!R.length,P=i==="card",B=i==="segment",T=!P&&!B&&this.justifyContent;h.value=[];const V=()=>{const c=l("div",{style:this.tabWrapperStyle,class:`${e}-tabs-wrapper`},T?null:l("div",{class:`${e}-tabs-scroll-padding`,style:b==="top"||b==="bottom"?{width:`${this.tabsPadding}px`}:{height:`${this.tabsPadding}px`}}),m?x.map((z,H)=>(h.value.push(z.props.name),ie(l(se,Object.assign({},z.props,{internalCreatedByPane:!0,internalLeftPadded:H!==0&&(!T||T==="center"||T==="start"||T==="end")}),z.children?{default:z.children.tab}:void 0)))):R.map((z,H)=>(h.value.push(z.props.name),ie(H!==0&&!T?we(z):z))),!v&&d&&P?ye(d,(m?x.length:R.length)!==0):null,T?null:l("div",{class:`${e}-tabs-scroll-padding`,style:{width:`${this.tabsPadding}px`}}));return l("div",{ref:"tabsElRef",class:`${e}-tabs-nav-scroll-content`},P&&d?l(ae,{onResize:this.handleTabsResize},{default:()=>c}):c,P?l("div",{class:`${e}-tabs-pad`}):null,P?null:l("div",{ref:"barElRef",class:`${e}-tabs-bar`}))},_=B?"top":b;return l("div",{class:[`${e}-tabs`,this.themeClass,`${e}-tabs--${i}-type`,`${e}-tabs--${w}-size`,T&&`${e}-tabs--flex`,`${e}-tabs--${_}`],style:this.cssVars},l("div",{class:[`${e}-tabs-nav--${i}-type`,`${e}-tabs-nav--${_}`,`${e}-tabs-nav`]},ge(k,c=>c&&l("div",{class:`${e}-tabs-nav__prefix`},c)),B?l(ae,{onResize:this.handleSegmentResize},{default:()=>l("div",{class:`${e}-tabs-rail`,ref:"tabsElRef"},l("div",{class:`${e}-tabs-capsule`,ref:"segmentCapsuleElRef"},l("div",{class:`${e}-tabs-wrapper`},l("div",{class:`${e}-tabs-tab`}))),m?x.map((c,z)=>(h.value.push(c.props.name),l(se,Object.assign({},c.props,{internalCreatedByPane:!0,internalLeftPadded:z!==0}),c.children?{default:c.children.tab}:void 0))):R.map((c,z)=>(h.value.push(c.props.name),z===0?c:we(c))))}):l(ae,{onResize:this.handleNavResize},{default:()=>l("div",{class:`${e}-tabs-nav-scroll-wrapper`,ref:"scrollWrapperElRef"},["top","bottom"].includes(_)?l(Ot,{ref:"xScrollInstRef",onScroll:this.handleScroll},{default:V}):l("div",{class:`${e}-tabs-nav-y-scroll`,onScroll:this.handleScroll,ref:"yScrollElRef"},V()))}),v&&d&&P?ye(d,!0):null,ge(A,c=>c&&l("div",{class:`${e}-tabs-nav__suffix`},c))),m&&(this.animated&&(_==="top"||_==="bottom")?l("div",{ref:"tabsPaneWrapperRef",style:g,class:[`${e}-tabs-pane-wrapper`,S]},me(x,this.mergedValue,this.renderedNames,this.onAnimationBeforeLeave,this.onAnimationEnter,this.onAnimationAfterEnter,this.animationDirection)):me(x,this.mergedValue,this.renderedNames)))}});function me(e,i,b,v,d,w,h){const C=[];return e.forEach(S=>{const{name:g,displayDirective:f,"display-directive":k}=S.props,A=R=>f===R||k===R,x=i===g;if(S.key!==void 0&&(S.key=g),x||A("show")||A("show:lazy")&&b.has(g)){b.has(g)||b.add(g);const R=!A("if");C.push(R?Lt(S,[[At,x]]):S)}}),h?l(Bt,{name:`${h}-transition`,onBeforeLeave:v,onEnter:d,onAfterEnter:w},{default:()=>C}):C}function ye(e,i){return l(se,{ref:"addTabInstRef",key:"__addable",name:"__addable",internalCreatedByPane:!0,internalAddable:!0,internalLeftPadded:i,disabled:typeof e=="object"&&e.disabled})}function we(e){const i=Et(e);return i.props?i.props.internalLeftPadded=!0:i.props={internalLeftPadded:!0},i}function ie(e){return Array.isArray(e.dynamicProps)?e.dynamicProps.includes("internalLeftPadded")||e.dynamicProps.push("internalLeftPadded"):e.dynamicProps=["internalLeftPadded"],e}export{se as _,Gt as a,Ut as b};
