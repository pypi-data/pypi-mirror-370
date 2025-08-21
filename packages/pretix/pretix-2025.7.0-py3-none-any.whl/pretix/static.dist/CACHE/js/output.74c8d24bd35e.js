var lookup='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';(function(exports){'use strict'
var Arr=(typeof Uint8Array!=='undefined')?Uint8Array:Array
var PLUS='+'.charCodeAt(0)
var SLASH='/'.charCodeAt(0)
var NUMBER='0'.charCodeAt(0)
var LOWER='a'.charCodeAt(0)
var UPPER='A'.charCodeAt(0)
var PLUS_URL_SAFE='-'.charCodeAt(0)
var SLASH_URL_SAFE='_'.charCodeAt(0)
function decode(elt){var code=elt.charCodeAt(0)
if(code===PLUS||code===PLUS_URL_SAFE)return 62
if(code===SLASH||code===SLASH_URL_SAFE)return 63
if(code<NUMBER)return-1
if(code<NUMBER+10)return code-NUMBER+26+26
if(code<UPPER+26)return code-UPPER
if(code<LOWER+26)return code-LOWER+26}
function b64ToByteArray(b64){var i,j,l,tmp,placeHolders,arr
if(b64.length%4>0){throw new Error('Invalid string. Length must be a multiple of 4')}
var len=b64.length
placeHolders=b64.charAt(len-2)==='='?2:b64.charAt(len-1)==='='?1:0
arr=new Arr(b64.length*3/4-placeHolders)
l=placeHolders>0?b64.length-4:b64.length
var L=0
function push(v){arr[L++]=v}
for(i=0,j=0;i<l;i+=4,j+=3){tmp=(decode(b64.charAt(i))<<18)|(decode(b64.charAt(i+1))<<12)|(decode(b64.charAt(i+2))<<6)|decode(b64.charAt(i+3))
push((tmp&0xFF0000)>>16)
push((tmp&0xFF00)>>8)
push(tmp&0xFF)}
if(placeHolders===2){tmp=(decode(b64.charAt(i))<<2)|(decode(b64.charAt(i+1))>>4)
push(tmp&0xFF)}else if(placeHolders===1){tmp=(decode(b64.charAt(i))<<10)|(decode(b64.charAt(i+1))<<4)|(decode(b64.charAt(i+2))>>2)
push((tmp>>8)&0xFF)
push(tmp&0xFF)}
return arr}
function uint8ToBase64(uint8){var i
var extraBytes=uint8.length%3
var output=''
var temp,length
function encode(num){return lookup.charAt(num)}
function tripletToBase64(num){return encode(num>>18&0x3F)+encode(num>>12&0x3F)+encode(num>>6&0x3F)+encode(num&0x3F)}
for(i=0,length=uint8.length-extraBytes;i<length;i+=3){temp=(uint8[i]<<16)+(uint8[i+1]<<8)+(uint8[i+2])
output+=tripletToBase64(temp)}
switch(extraBytes){case 1:temp=uint8[uint8.length-1]
output+=encode(temp>>2)
output+=encode((temp<<4)&0x3F)
output+='=='
break
case 2:temp=(uint8[uint8.length-2]<<8)+(uint8[uint8.length-1])
output+=encode(temp>>10)
output+=encode((temp>>4)&0x3F)
output+=encode((temp<<2)&0x3F)
output+='='
break
default:break}
return output}
exports.toByteArray=b64ToByteArray
exports.fromByteArray=uint8ToBase64}(typeof exports==='undefined'?(this.base64js={}):exports));function b64enc(buf){return base64js.fromByteArray(buf).replace(/\+/g,"-").replace(/\//g,"_").replace(/=/g,"");}
function b64RawEnc(buf){return base64js.fromByteArray(buf).replace(/\+/g,"-").replace(/\//g,"_");}
function hexEncode(buf){return Array.from(buf).map(function(x){return("0"+x.toString(16)).substr(-2);}).join("");}
async function fetch_json(url,options){const response=await fetch(url,options);const body=await response.json();if(body.fail)
throw body.fail;return body;}
const transformCredentialCreateOptions=function(credentialCreateOptionsFromServer){let{challenge,user,excludeCredentials}=credentialCreateOptionsFromServer;user.id=user.id.replace(/\_/g,"/").replace(/\-/g,"+");user.id=Uint8Array.from(atob(user.id),c=>c.charCodeAt(0));challenge=challenge.replace(/\_/g,"/").replace(/\-/g,"+");challenge=Uint8Array.from(atob(challenge),c=>c.charCodeAt(0));excludeCredentials=excludeCredentials.map(credentialDescriptor=>{let{id}=credentialDescriptor;id=id.replace(/\_/g,"/").replace(/\-/g,"+");id=Uint8Array.from(atob(id),c=>c.charCodeAt(0));return Object.assign({},credentialDescriptor,{id});});const transformedCredentialCreateOptions=Object.assign({},credentialCreateOptionsFromServer,{challenge,user,excludeCredentials});return transformedCredentialCreateOptions;};const transformNewAssertionForServer=(newAssertion)=>{const attObj=new Uint8Array(newAssertion.response.attestationObject);const clientDataJSON=new Uint8Array(newAssertion.response.clientDataJSON);const rawId=new Uint8Array(newAssertion.rawId);const transports=newAssertion.response.getTransports();const authenticatorAttachment=newAssertion.authenticatorAttachment;const registrationClientExtensions=newAssertion.getClientExtensionResults();return{id:newAssertion.id,rawId:b64enc(rawId),response:{attestationObject:b64enc(attObj),clientDataJSON:b64enc(clientDataJSON),transports:transports,},type:newAssertion.type,clientExtensionResults:JSON.stringify(registrationClientExtensions),authenticatorAttachment:authenticatorAttachment,};};const transformCredentialRequestOptions=(credentialRequestOptionsFromServer)=>{let{challenge,allowCredentials}=credentialRequestOptionsFromServer;challenge=challenge.replace(/\_/g,"/").replace(/\-/g,"+");challenge=Uint8Array.from(atob(challenge),c=>c.charCodeAt(0));allowCredentials=allowCredentials.map(credentialDescriptor=>{let{id}=credentialDescriptor;id=id.replace(/\_/g,"/").replace(/\-/g,"+");id=Uint8Array.from(atob(id),c=>c.charCodeAt(0));return Object.assign({},credentialDescriptor,{id});});const transformedCredentialRequestOptions=Object.assign({},credentialRequestOptionsFromServer,{challenge,allowCredentials});return transformedCredentialRequestOptions;};const transformAssertionForServer=(newAssertion)=>{const authData=new Uint8Array(newAssertion.response.authenticatorData);const clientDataJSON=new Uint8Array(newAssertion.response.clientDataJSON);const rawId=new Uint8Array(newAssertion.rawId);const sig=new Uint8Array(newAssertion.response.signature);const userHandle=new Uint8Array(newAssertion.response.userHandle);const assertionClientExtensions=newAssertion.getClientExtensionResults();const authenticatorAttachment=newAssertion.authenticatorAttachment;return{id:newAssertion.id,rawId:b64enc(rawId),type:newAssertion.type,response:{authenticatorData:b64RawEnc(authData),clientDataJSON:b64RawEnc(clientDataJSON),signature:b64RawEnc(sig),userHandle:b64RawEnc(userHandle),},authenticatorAttachment:authenticatorAttachment,clientExtensionResults:JSON.stringify(assertionClientExtensions)};};const startRegister=async(e)=>{const publicKeyCredentialCreateOptions=transformCredentialCreateOptions(JSON.parse($("#webauthn-enroll").text()));let credential;try{credential=await navigator.credentials.create({publicKey:publicKeyCredentialCreateOptions});}catch(err){$("#webauthn-error").removeClass("hidden");return console.error("Error creating credential:",err);}
const newAssertionForServer=transformNewAssertionForServer(credential);$("#webauthn-response").val(JSON.stringify(newAssertionForServer));$("#webauthn-form").submit();};const startLogin=async(e)=>{const transformedCredentialRequestOptions=transformCredentialRequestOptions(JSON.parse($("#webauthn-login").text()));console.log(transformedCredentialRequestOptions);let assertion;try{assertion=await navigator.credentials.get({publicKey:transformedCredentialRequestOptions,});}catch(err){$("#webauthn-error").removeClass("hidden");return console.error("Error when creating credential:",err);}
const transformedAssertionForServer=transformAssertionForServer(assertion);$("input, select, textarea").prop("required",false);$("#webauthn-response, #id_password").val(JSON.stringify(transformedAssertionForServer));$("#webauthn-form").submit();};$(function(){$("#webauthn-progress").hide();if($("#webauthn-enroll").length){$("#webauthn-progress").show();startRegister();}else if($("#webauthn-login").length){$("#webauthn-progress").show();startLogin();}});;