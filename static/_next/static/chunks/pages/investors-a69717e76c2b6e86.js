(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[234],{2186:function(e,n,s){"use strict";var t=s(8175),r=s(5893);n.Z=(0,t.Z)((0,r.jsx)("path",{d:"M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"}),"Visibility")},1239:function(e,n,s){(window.__NEXT_P=window.__NEXT_P||[]).push(["/investors",function(){return s(6373)}])},6373:function(e,n,s){"use strict";s.r(n),s.d(n,{default:function(){return q}});var t=s(5893),r=s(7294),o=s(5697),i=s.n(o),c=s(7074),a=s(2097),l=s(120),d=s(244),h=s(3978),p=s(9807),x=s(7272),j=s(4026),u=s(6777),Z=s(3212),m=s(2773),g=s(9417),y=s(1401),f=s(562),w=s(8066),b=s(6172),v=s(8317),_=s(1290),P=s(9072),C=s(784),k=s(9630),S=s(5084),T=s(1664),N=s.n(T),I=s(2186),z=s(1163),E=s(594),M=s(1955);let R=(0,c.ZP)(x.Z)(e=>{let{theme:n}=e;return{["&.".concat(j.Z.head)]:{backgroundColor:n.palette.primary.dark,color:n.palette.common.white},["&.".concat(j.Z.body)]:{fontSize:14}}});function A(e){let n=(0,a.Z)(),{count:s,page:r,rowsPerPage:o,onPageChange:i}=e,c=e=>{i(e,0)},d=e=>{i(e,r-1)},h=e=>{i(e,r+1)},p=e=>{i(e,Math.max(0,Math.ceil(s/o)-1))};return(0,t.jsxs)(l.Z,{sx:{flexShrink:0,ml:2.5},children:[(0,t.jsx)(f.Z,{onClick:c,disabled:0===r,"aria-label":"first page",children:"rtl"===n.direction?(0,t.jsx)(_.Z,{}):(0,t.jsx)(w.Z,{})}),(0,t.jsx)(f.Z,{onClick:d,disabled:0===r,"aria-label":"previous page",children:"rtl"===n.direction?(0,t.jsx)(v.Z,{}):(0,t.jsx)(b.Z,{})}),(0,t.jsx)(f.Z,{onClick:h,disabled:r>=Math.ceil(s/o)-1,"aria-label":"next page",children:"rtl"===n.direction?(0,t.jsx)(b.Z,{}):(0,t.jsx)(v.Z,{})}),(0,t.jsx)(f.Z,{onClick:p,disabled:r>=Math.ceil(s/o)-1,"aria-label":"last page",children:"rtl"===n.direction?(0,t.jsx)(w.Z,{}):(0,t.jsx)(_.Z,{})})]})}function q(){let[e,n]=(0,r.useState)(0),[s,o]=(0,r.useState)(5),[i,c]=(0,r.useState)([]),a=e>0?Math.max(0,(1+e)*s-i.length):0,j=(e,s)=>{n(s)},f=e=>{o(parseInt(e.target.value,10)),n(0)},w=M.Z.get("accessToken"),b=M.Z.get("companyName"),v=(0,z.useRouter)(),[_,T]=(0,r.useState)(!0);(0,r.useEffect)(()=>{let e=M.Z.get("accessToken");e||v.push("/")},[v]);let q=()=>{E.Z.get("".concat("http://minkyaa.pythonanywhere.com/admin-api","/get-investors-warehouses/?company_type=").concat(b),{headers:{Authorization:"Bearer ".concat(w),"Content-Type":"application/json"}}).then(e=>{console.log("investors res",e.data.response),e&&(c(e.data.response),T(!1))}).catch(e=>{console.log("investors err",e)})};return(0,r.useEffect)(()=>{q()},[]),console.log("investors",i),(0,t.jsx)(P.ZP,{container:!0,spacing:2,justifyContent:"center",sx:{padding:3},children:(0,t.jsxs)(P.ZP,{item:!0,lg:12,xs:11,children:[(0,t.jsx)(C.Z,{}),(0,t.jsx)("h1",{children:"Investors"}),(0,t.jsxs)(y.Z,{variant:"outlined",sx:{padding:"1em",width:"100%"},children:[(0,t.jsx)(P.ZP,{item:!0,lg:12,xs:11,children:(0,t.jsxs)(l.Z,{sx:{display:"flex",justifyContent:"space-between",alignItems:"center"},children:[(0,t.jsx)(k.Z,{variant:"subtitle1",sx:{fontSize:"20px"},gutterBottom:!0,children:"Investors List"}),(0,t.jsx)(N(),{href:"/investors/addInvestors",children:(0,t.jsx)(S.Z,{variant:"contained",children:"+ Add Investor"})})]})}),(0,t.jsx)(P.ZP,{item:!0,lg:12,xs:11,children:(0,t.jsx)(u.Z,{component:y.Z,sx:{marginTop:"15px"},children:(0,t.jsxs)(d.Z,{sx:{minWidth:500},"aria-label":"custom pagination table",children:[(0,t.jsx)(h.Z,{children:(0,t.jsxs)(g.Z,{children:[(0,t.jsx)(R,{children:"No."}),(0,t.jsx)(R,{children:"Property Name"}),(0,t.jsx)(R,{children:"Property Type"}),(0,t.jsx)(R,{children:"Property Survay Number"}),(0,t.jsx)(R,{children:"Address"}),(0,t.jsx)(R,{children:"City"}),(0,t.jsx)(R,{children:"State"}),(0,t.jsx)(R,{children:"Country"}),(0,t.jsx)(R,{children:"Total Galas"}),(0,t.jsx)(R,{children:"Total Investors"}),(0,t.jsx)(R,{children:"Details"})]})}),(0,t.jsxs)(p.Z,{children:[(s>0?i.slice(e*s,e*s+s):i).map((e,n)=>(0,t.jsxs)(g.Z,{children:[(0,t.jsx)(x.Z,{component:"th",scope:"row",children:n+1}),(0,t.jsx)(x.Z,{component:"th",scope:"row",children:e.property_name}),(0,t.jsx)(x.Z,{component:"th",scope:"row",children:e.property_type}),(0,t.jsx)(x.Z,{component:"th",scope:"row",children:e.property_survey_number}),(0,t.jsx)(x.Z,{component:"th",scope:"row",children:e.address}),(0,t.jsx)(x.Z,{component:"th",scope:"row",children:e.city}),(0,t.jsx)(x.Z,{component:"th",scope:"row",children:e.state}),(0,t.jsx)(x.Z,{component:"th",scope:"row",children:e.country}),(0,t.jsx)(x.Z,{component:"th",scope:"row",children:e.total_number_of_galas}),(0,t.jsx)(x.Z,{component:"th",scope:"row",children:e.total_number_of_investors}),(0,t.jsx)(x.Z,{component:"th",scope:"row",children:(0,t.jsx)(N(),{href:"/investors/".concat(e.uid),style:{textDecoration:"none"},children:(0,t.jsx)(S.Z,{size:"small",variant:"text",sx:{textTransform:"lowercase"},endIcon:(0,t.jsx)(I.Z,{}),children:"view"})})})]},n)),a>0&&(0,t.jsx)(g.Z,{style:{height:53*a},children:(0,t.jsx)(x.Z,{colSpan:6})})]}),(0,t.jsx)(Z.Z,{children:(0,t.jsx)(g.Z,{children:(0,t.jsx)(m.Z,{rowsPerPageOptions:[5,10,25,{label:"All",value:-1}],colSpan:12,count:i.length,rowsPerPage:s,page:e,SelectProps:{inputProps:{"aria-label":"rows per page"},native:!0},onPageChange:j,onRowsPerPageChange:f,ActionsComponent:A})})})]})})})]})]})})}A.propTypes={count:i().number.isRequired,onPageChange:i().func.isRequired,page:i().number.isRequired,rowsPerPage:i().number.isRequired}}},function(e){e.O(0,[527,774,888,179],function(){return e(e.s=1239)}),_N_E=e.O()}]);