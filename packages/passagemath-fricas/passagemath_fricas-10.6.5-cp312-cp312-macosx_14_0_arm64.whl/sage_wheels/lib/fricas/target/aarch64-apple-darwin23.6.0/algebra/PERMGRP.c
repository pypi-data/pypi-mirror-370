/*      Compiler: ECL 24.5.10                                         */
/*      Date: 2025/8/17 08:26 (yyyy/mm/dd)                            */
/*      Machine: Darwin 23.6.0 arm64                                  */
/*      Source: /Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/pre-generated/src/algebra/PERMGRP.lsp */
#include <ecl/ecl-cmp.h>
#include "/Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/_build/target/aarch64-apple-darwin23.6.0/algebra/PERMGRP.eclh"
/*      function definition for PERMGRP;shortenWord                   */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L526_permgrp_shortenword_(cl_object v1_lw_, cl_object v2_gp_, cl_object v3_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_do_res_;
  cl_object v5_flag1_;
  cl_object v6_newlw_;
  cl_object v7;
  cl_object v8_anzahl_;
  cl_object v9_flag2_;
  cl_object v10_res_;
  cl_object v11_test_;
  cl_object v12;
  cl_object v13_el_;
  cl_object v14_pos_;
  cl_object v15;
  cl_object v16_i_;
  cl_object v17_orderlist_;
  cl_object v18;
  cl_object v19_gen_;
  cl_object v20;
  cl_object v21_gpgens_;
  v4_do_res_ = ECL_NIL;
  v5_flag1_ = ECL_NIL;
  v6_newlw_ = ECL_NIL;
  v7 = ECL_NIL;
  v8_anzahl_ = ecl_make_fixnum(0);
  v9_flag2_ = ECL_NIL;
  v10_res_ = ECL_NIL;
  v11_test_ = ecl_make_fixnum(0);
  v12 = ECL_NIL;
  v13_el_ = ECL_NIL;
  v14_pos_ = ecl_make_fixnum(0);
  v15 = ECL_NIL;
  v16_i_ = ECL_NIL;
  v17_orderlist_ = ECL_NIL;
  v18 = ECL_NIL;
  v19_gen_ = ECL_NIL;
  v20 = ECL_NIL;
  v21_gpgens_ = ECL_NIL;
  {
   cl_object v22;
   v22 = (v3_)->vector.self.t[9];
   T0 = _ecl_car(v22);
   T1 = _ecl_cdr(v22);
   v21_gpgens_ = (cl_env_copy->function=T0)->cfun.entry(2, v2_gp_, T1);
  }
  v20 = ECL_NIL;
  v19_gen_ = ECL_NIL;
  v18 = v21_gpgens_;
L27:;
  if (ECL_ATOM(v18)) { goto L35; }
  v19_gen_ = _ecl_car(v18);
  goto L33;
L35:;
  goto L28;
L33:;
  {
   cl_object v22;
   v22 = (v3_)->vector.self.t[12];
   T1 = _ecl_car(v22);
   T2 = _ecl_cdr(v22);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, v19_gen_, T2);
  }
  v20 = CONS(T0,v20);
  goto L39;
L39:;
  v18 = _ecl_cdr(v18);
  goto L27;
L28:;
  v17_orderlist_ = cl_nreverse(v20);
  goto L24;
L24:;
  {
   cl_object v22;
   v22 = (v3_)->vector.self.t[14];
   T0 = _ecl_car(v22);
   T1 = _ecl_cdr(v22);
   v6_newlw_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_lw_, T1);
  }
  v16_i_ = ecl_make_fixnum(1);
  v15 = ecl_make_fixnum(ecl_length(v17_orderlist_));
L54:;
  if (!((ecl_fixnum(v16_i_))>(ecl_fixnum(v15)))) { goto L60; }
  goto L55;
L60:;
  {
   cl_object v22;
   v22 = (v3_)->vector.self.t[16];
   T1 = _ecl_car(v22);
   T2 = _ecl_cdr(v22);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, v17_orderlist_, v16_i_, T2);
  }
  if (!((T0)==(ecl_make_fixnum(1)))) { goto L62; }
L68:;
  {
   cl_object v22;
   v22 = (v3_)->vector.self.t[18];
   T1 = _ecl_car(v22);
   T2 = _ecl_cdr(v22);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, v16_i_, v6_newlw_, T2);
  }
  if (!(T0==ECL_NIL)) { goto L70; }
  goto L69;
L70:;
  {
   cl_object v22;
   v22 = (v3_)->vector.self.t[19];
   T0 = _ecl_car(v22);
   T1 = _ecl_cdr(v22);
   v14_pos_ = (cl_env_copy->function=T0)->cfun.entry(3, v16_i_, v6_newlw_, T1);
  }
  {
   cl_object v22;
   v22 = (v3_)->vector.self.t[20];
   T0 = _ecl_car(v22);
   T1 = _ecl_cdr(v22);
   v6_newlw_ = (cl_env_copy->function=T0)->cfun.entry(3, v6_newlw_, v14_pos_, T1);
  }
  goto L75;
L75:;
  goto L68;
L69:;
  goto L62;
L62:;
  v16_i_ = ecl_make_fixnum((ecl_fixnum(v16_i_))+1);
  goto L54;
L55:;
  goto L53;
L53:;
  {
   cl_object v22;
   v22 = (v3_)->vector.self.t[21];
   T1 = _ecl_car(v22);
   T2 = _ecl_cdr(v22);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, v6_newlw_, T2);
  }
  if (!(ecl_lower(T0,ecl_make_fixnum(2)))) { goto L92; }
  value0 = v6_newlw_;
  cl_env_copy->nvalues = 1;
  return value0;
L92:;
  if (Null(v6_newlw_)) { goto L99; }
  v11_test_ = _ecl_car(v6_newlw_);
  goto L98;
L99:;
  v11_test_ = ecl_function_dispatch(cl_env_copy,VV[87])(0) /*  FIRST_ERROR */;
L98:;
  v8_anzahl_ = ecl_make_fixnum(0);
  v5_flag1_ = ECL_T;
  v4_do_res_ = ECL_NIL;
L108:;
  if (!(v5_flag1_==ECL_NIL)) { goto L110; }
  goto L109;
L110:;
  if (Null(v6_newlw_)) { goto L115; }
  v11_test_ = _ecl_car(v6_newlw_);
  goto L114;
L115:;
  v11_test_ = ecl_function_dispatch(cl_env_copy,VV[87])(0) /*  FIRST_ERROR */;
L114:;
  v8_anzahl_ = ecl_make_fixnum(1);
  if (Null(v4_do_res_)) { goto L119; }
  v10_res_ = ecl_list1(v11_test_);
L119:;
  v9_flag2_ = ECL_T;
  v13_el_ = ECL_NIL;
  v12 = v6_newlw_;
L125:;
  if (ECL_ATOM(v12)) { goto L133; }
  v13_el_ = _ecl_car(v12);
  if (!(v9_flag2_==ECL_NIL)) { goto L131; }
  goto L132;
L133:;
L132:;
  goto L126;
L131:;
  if (Null(v4_do_res_)) { goto L139; }
  v10_res_ = CONS(v13_el_,v10_res_);
L139:;
  v8_anzahl_ = ecl_plus(v8_anzahl_,ecl_make_fixnum(1));
  if (!((v8_anzahl_)==(ecl_make_fixnum(1)))) { goto L145; }
  v11_test_ = v13_el_;
  goto L138;
L145:;
  {
   cl_object v22;
   v22 = (v3_)->vector.self.t[23];
   T0 = _ecl_car(v22);
   T1 = _ecl_cdr(v22);
   if (Null((cl_env_copy->function=T0)->cfun.entry(3, v11_test_, v13_el_, T1))) { goto L148; }
  }
  v11_test_ = v13_el_;
  v8_anzahl_ = ecl_make_fixnum(1);
  goto L138;
L148:;
  {
   cl_object v22;
   v22 = (v3_)->vector.self.t[16];
   T1 = _ecl_car(v22);
   T2 = _ecl_cdr(v22);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, v17_orderlist_, v11_test_, T2);
  }
  if (!(ecl_eql(v8_anzahl_,T0))) { goto L138; }
  if (Null(v4_do_res_)) { goto L165; }
  {
   cl_object v22;
   v22 = (v3_)->vector.self.t[24];
   T0 = _ecl_car(v22);
   T1 = _ecl_cdr(v22);
   v10_res_ = (cl_env_copy->function=T0)->cfun.entry(3, v10_res_, v8_anzahl_, T1);
  }
  goto L164;
L165:;
  v9_flag2_ = ECL_NIL;
L164:;
  v8_anzahl_ = ecl_make_fixnum(0);
  v7 = ecl_make_fixnum(0);
  goto L163;
L163:;
  goto L156;
L156:;
  goto L138;
L138:;
  v12 = _ecl_cdr(v12);
  goto L125;
L126:;
  goto L124;
L124:;
  if (Null(v4_do_res_)) { goto L178; }
  v6_newlw_ = cl_nreverse(v10_res_);
L178:;
  v5_flag1_ = v4_do_res_;
  v4_do_res_ = ecl_make_bool(v9_flag2_==ECL_NIL);
  goto L112;
L112:;
  goto L108;
L109:;
  goto L107;
L107:;
  value0 = v6_newlw_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for PERMGRP;times!                        */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L527_permgrp_times__(cl_object v1_res_, cl_object v2_p_, cl_object v3_q_, cl_object v4_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5;
  cl_object v6_i_;
  cl_object v7_degree_;
  v5 = ECL_NIL;
  v6_i_ = ECL_NIL;
  v7_degree_ = ecl_make_fixnum(0);
  {
   cl_object v8;
   v8 = (v4_)->vector.self.t[26];
   T0 = _ecl_car(v8);
   T1 = _ecl_cdr(v8);
   v7_degree_ = (cl_env_copy->function=T0)->cfun.entry(2, v2_p_, T1);
  }
  v6_i_ = ecl_make_fixnum(1);
  v5 = v7_degree_;
L9:;
  if (!((ecl_fixnum(v6_i_))>(ecl_fixnum(v5)))) { goto L15; }
  goto L10;
L15:;
  {
   cl_fixnum v8;
   v8 = (ecl_fixnum(v6_i_))-(1);
   {
    cl_fixnum v9;
    {
     cl_fixnum v10;
     v10 = (ecl_fixnum(v6_i_))-(1);
     v9 = ecl_fixnum(ecl_aref_unsafe(v3_q_,v10));
    }
    {
     cl_fixnum v10;
     v10 = (v9)-(1);
     T0 = ecl_aref_unsafe(v2_p_,v10);
    }
   }
   (v1_res_)->vector.self.t[v8]= T0;
   goto L17;
  }
L17:;
  v6_i_ = ecl_make_fixnum((ecl_fixnum(v6_i_))+1);
  goto L9;
L10:;
  value0 = ECL_NIL;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for PERMGRP;times                         */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L528_permgrp_times_(cl_object v1_p_, cl_object v2_q_, cl_object v3_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_res_;
  cl_object v5_degree_;
  v4_res_ = ECL_NIL;
  v5_degree_ = ecl_make_fixnum(0);
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[26];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   v5_degree_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_p_, T1);
  }
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[27];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   v4_res_ = (cl_env_copy->function=T0)->cfun.entry(3, v5_degree_, ecl_make_fixnum(0), T1);
  }
  L527_permgrp_times__(v4_res_, v1_p_, v2_q_, v3_);
  value0 = v4_res_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for PERMGRP;inv                           */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L529_permgrp_inv_(cl_object v1_p_, cl_object v2_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3;
  cl_object v4_i_;
  cl_object v5_q_;
  cl_object v6_degree_;
  v3 = ECL_NIL;
  v4_i_ = ECL_NIL;
  v5_q_ = ECL_NIL;
  v6_degree_ = ecl_make_fixnum(0);
  {
   cl_object v7;
   v7 = (v2_)->vector.self.t[26];
   T0 = _ecl_car(v7);
   T1 = _ecl_cdr(v7);
   v6_degree_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_p_, T1);
  }
  {
   cl_object v7;
   v7 = (v2_)->vector.self.t[27];
   T0 = _ecl_car(v7);
   T1 = _ecl_cdr(v7);
   v5_q_ = (cl_env_copy->function=T0)->cfun.entry(3, v6_degree_, ecl_make_fixnum(0), T1);
  }
  v4_i_ = ecl_make_fixnum(1);
  v3 = v6_degree_;
L14:;
  if (!((ecl_fixnum(v4_i_))>(ecl_fixnum(v3)))) { goto L20; }
  goto L15;
L20:;
  {
   cl_fixnum v7;
   {
    cl_fixnum v8;
    v8 = (ecl_fixnum(v4_i_))-(1);
    v7 = ecl_fixnum(ecl_aref_unsafe(v1_p_,v8));
   }
   {
    cl_fixnum v8;
    v8 = (v7)-(1);
    (v5_q_)->vector.self.t[v8]= v4_i_;
    goto L22;
   }
  }
L22:;
  v4_i_ = ecl_make_fixnum((ecl_fixnum(v4_i_))+1);
  goto L14;
L15:;
  goto L13;
L13:;
  value0 = v5_q_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for PERMGRP;testIdentity                  */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L530_permgrp_testidentity_(cl_object v1_p_, cl_object v2_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3;
  cl_object v4;
  cl_object v5;
  cl_object v6_i_;
  cl_object v7_degree_;
  v3 = ECL_NIL;
  v4 = ECL_NIL;
  v5 = ECL_NIL;
  v6_i_ = ECL_NIL;
  v7_degree_ = ecl_make_fixnum(0);
  {
   cl_object v8;
   v8 = (v2_)->vector.self.t[26];
   T0 = _ecl_car(v8);
   T1 = _ecl_cdr(v8);
   v7_degree_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_p_, T1);
  }
  v6_i_ = ecl_make_fixnum(1);
  v5 = v7_degree_;
L15:;
  if (!((ecl_fixnum(v6_i_))>(ecl_fixnum(v5)))) { goto L21; }
  goto L16;
L21:;
  {
   cl_object v8;
   v8 = (v2_)->vector.self.t[23];
   T0 = _ecl_car(v8);
   {
    cl_fixnum v9;
    v9 = (ecl_fixnum(v6_i_))-(1);
    T1 = ecl_aref_unsafe(v1_p_,v9);
   }
   T2 = _ecl_cdr(v8);
   if (Null((cl_env_copy->function=T0)->cfun.entry(3, T1, v6_i_, T2))) { goto L23; }
  }
  v4 = ECL_NIL;
  goto L6;
  goto L13;
L23:;
  v6_i_ = ecl_make_fixnum((ecl_fixnum(v6_i_))+1);
  goto L15;
L16:;
  goto L12;
L13:;
  goto L12;
L12:;
  value0 = ECL_T;
  cl_env_copy->nvalues = 1;
  return value0;
L6:;
  value0 = v4;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for PERMGRP;cosetRep1                     */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L531_permgrp_cosetrep1_(cl_object v1_ppt_, cl_object v2_do_words_, cl_object v3_o_, cl_object v4_grpv_, cl_object v5_wordv_, cl_object v6_)
{
 cl_object T0, T1, T2, T3;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v7;
  cl_object v8_p_;
  cl_object v9_word_;
  cl_object v10_xelt_;
  cl_object v11_tmpv_;
  cl_object v12__g25_;
  cl_object v13__g24_;
  cl_object v14_x_;
  cl_object v15_osvc_;
  cl_object v16;
  cl_object v17;
  cl_object v18_n_;
  cl_object v19;
  cl_object v20_degree_;
  v7 = ECL_NIL;
  v8_p_ = ecl_make_fixnum(0);
  v9_word_ = ECL_NIL;
  v10_xelt_ = ECL_NIL;
  v11_tmpv_ = ECL_NIL;
  v12__g25_ = ECL_NIL;
  v13__g24_ = ECL_NIL;
  v14_x_ = ECL_NIL;
  v15_osvc_ = ECL_NIL;
  v16 = ECL_NIL;
  v17 = ECL_NIL;
  v18_n_ = ECL_NIL;
  v19 = ECL_NIL;
  v20_degree_ = ecl_make_fixnum(0);
  {
   cl_fixnum v21;
   v21 = (v4_grpv_)->vector.fillp;
   if (!((v21)==(0))) { goto L17; }
  }
  value0 = ecl_function_dispatch(cl_env_copy,VV[93])(1, VV[6]) /*  error */;
  return value0;
L17:;
  {
   cl_object v21;
   v21 = (v6_)->vector.self.t[26];
   T0 = _ecl_car(v21);
   {
    cl_object v22;
    v22 = (v6_)->vector.self.t[29];
    T2 = _ecl_car(v22);
    T3 = _ecl_cdr(v22);
    T1 = (cl_env_copy->function=T2)->cfun.entry(3, v4_grpv_, ecl_make_fixnum(1), T3);
   }
   T2 = _ecl_cdr(v21);
   v20_degree_ = (cl_env_copy->function=T0)->cfun.entry(2, T1, T2);
  }
  v19 = ecl_function_dispatch(cl_env_copy,VV[94])(1, v20_degree_) /*  GETREFV */;
  v18_n_ = ecl_make_fixnum(1);
  v17 = v20_degree_;
  v16 = ecl_make_fixnum(0);
L31:;
  if (!((ecl_fixnum(v18_n_))>(ecl_fixnum(v17)))) { goto L39; }
  goto L32;
L39:;
  ecl_elt_set(v19,ecl_fixnum(v16),v18_n_);
  goto L41;
L41:;
  {
   cl_fixnum v21;
   v21 = (ecl_fixnum(v16))+1;
   v18_n_ = ecl_make_fixnum((ecl_fixnum(v18_n_))+1);
   v16 = ecl_make_fixnum(v21);
  }
  goto L31;
L32:;
  goto L30;
L30:;
  v10_xelt_ = v19;
  v9_word_ = ECL_NIL;
  v15_osvc_ = ECL_CONS_CDR(v3_o_);
  {
   cl_fixnum v21;
   v21 = (ecl_fixnum(v1_ppt_))-(1);
   v8_p_ = ecl_aref_unsafe(v15_osvc_,v21);
  }
  if (!(ecl_lower(v8_p_,ecl_make_fixnum(0)))) { goto L57; }
  v7 = CONS(v10_xelt_,v9_word_);
  goto L15;
L57:;
  {
   cl_object v21;
   v21 = (v6_)->vector.self.t[27];
   T0 = _ecl_car(v21);
   T1 = _ecl_cdr(v21);
   v11_tmpv_ = (cl_env_copy->function=T0)->cfun.entry(3, v20_degree_, ecl_make_fixnum(0), T1);
  }
L66:;
  {
   cl_fixnum v21;
   v21 = (ecl_fixnum(v8_p_))-(1);
   v14_x_ = ecl_aref_unsafe(v4_grpv_,v21);
  }
  L527_permgrp_times__(v11_tmpv_, v14_x_, v10_xelt_, v6_);
  v13__g24_ = v10_xelt_;
  v12__g25_ = v11_tmpv_;
  v11_tmpv_ = v13__g24_;
  v10_xelt_ = v12__g25_;
  if (Null(v2_do_words_)) { goto L81; }
  {
   cl_object v21;
   v21 = (v6_)->vector.self.t[32];
   T0 = _ecl_car(v21);
   {
    cl_object v22;
    v22 = (v6_)->vector.self.t[31];
    T2 = _ecl_car(v22);
    T3 = _ecl_cdr(v22);
    T1 = (cl_env_copy->function=T2)->cfun.entry(3, v5_wordv_, v8_p_, T3);
   }
   T2 = _ecl_cdr(v21);
   v9_word_ = (cl_env_copy->function=T0)->cfun.entry(3, T1, v9_word_, T2);
  }
L81:;
  {
   cl_fixnum v21;
   v21 = (ecl_fixnum(v1_ppt_))-(1);
   v1_ppt_ = ecl_aref_unsafe(v14_x_,v21);
  }
  {
   cl_fixnum v21;
   v21 = (ecl_fixnum(v1_ppt_))-(1);
   v8_p_ = ecl_aref_unsafe(v15_osvc_,v21);
  }
  if (!(ecl_lower(v8_p_,ecl_make_fixnum(0)))) { goto L69; }
  v7 = CONS(v10_xelt_,v9_word_);
  goto L15;
L69:;
  goto L66;
  value0 = ECL_NIL;
  cl_env_copy->nvalues = 1;
  return value0;
L15:;
  value0 = v7;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for PERMGRP;strip1                        */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L532_permgrp_strip1_(cl_object v1_element_, cl_object v2_orbit_, cl_object v3_group_, cl_object v4_words_, cl_object v5_)
{
 cl_object T0, T1, T2, T3;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v6_cr_;
  cl_object v7_point_;
  cl_object v8_wordv_;
  cl_object v9_do_words_;
  cl_object v10_grpv_;
  v6_cr_ = ECL_NIL;
  v7_point_ = ecl_make_fixnum(0);
  v8_wordv_ = ECL_NIL;
  v9_do_words_ = ECL_NIL;
  v10_grpv_ = ECL_NIL;
  {
   cl_object v11;
   v11 = (v5_)->vector.self.t[34];
   T0 = _ecl_car(v11);
   T1 = _ecl_cdr(v11);
   v10_grpv_ = (cl_env_copy->function=T0)->cfun.entry(2, v3_group_, T1);
  }
  v8_wordv_ = si_make_vector(ECL_T, ecl_make_fixnum(0), ECL_NIL, ECL_NIL, ECL_NIL, ecl_make_fixnum(0));
  {
   bool v11;
   v11 = v4_words_==ECL_NIL;
   v9_do_words_ = ecl_make_bool(ecl_make_bool(v11)==ECL_NIL);
  }
  if (Null(v9_do_words_)) { goto L14; }
  {
   cl_object v11;
   v11 = (v5_)->vector.self.t[36];
   T0 = _ecl_car(v11);
   T1 = _ecl_cdr(v11);
   v8_wordv_ = (cl_env_copy->function=T0)->cfun.entry(2, v4_words_, T1);
  }
L14:;
  {
   cl_fixnum v11;
   {
    cl_object v12;
    v12 = (v5_)->vector.self.t[37];
    T0 = _ecl_car(v12);
    T1 = ECL_CONS_CAR(v2_orbit_);
    T2 = _ecl_cdr(v12);
    v11 = ecl_fixnum((cl_env_copy->function=T0)->cfun.entry(3, T1, ecl_make_fixnum(1), T2));
   }
   {
    cl_fixnum v12;
    v12 = (v11)-(1);
    v7_point_ = ecl_aref_unsafe(v1_element_,v12);
   }
  }
  v6_cr_ = L531_permgrp_cosetrep1_(v7_point_, v9_do_words_, v2_orbit_, v10_grpv_, v8_wordv_, v5_);
  T0 = ECL_CONS_CAR(v6_cr_);
  T1 = L528_permgrp_times_(T0, v1_element_, v5_);
  T2 = ECL_CONS_CDR(v6_cr_);
  T3 = cl_reverse(T2);
  value0 = CONS(T1,T3);
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for PERMGRP;strip                         */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L533_permgrp_strip_(cl_object v1_z_, cl_object v2_i_, cl_object v3_do_words_, cl_object v4_orbs_, cl_object v5_grpv_, cl_object v6_wordv_, cl_object v7_)
{
 cl_object T0, T1, T2, T3;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v8_word_;
  cl_object v9_tmpv_;
  cl_object v10__g38_;
  cl_object v11__g37_;
  cl_object v12_ee_;
  cl_object v13_noresult_;
  cl_object v14;
  cl_object v15_entry_;
  cl_object v16_p_;
  cl_object v17_s_;
  cl_object v18_orbj_;
  cl_object v19_j_;
  cl_object v20_degree_;
  v8_word_ = ECL_NIL;
  v9_tmpv_ = ECL_NIL;
  v10__g38_ = ECL_NIL;
  v11__g37_ = ECL_NIL;
  v12_ee_ = ECL_NIL;
  v13_noresult_ = ECL_NIL;
  v14 = ECL_NIL;
  v15_entry_ = ecl_make_fixnum(0);
  v16_p_ = ecl_make_fixnum(0);
  v17_s_ = ECL_NIL;
  v18_orbj_ = ECL_NIL;
  v19_j_ = ECL_NIL;
  v20_degree_ = ecl_make_fixnum(0);
  {
   cl_object v21;
   v21 = (v7_)->vector.self.t[26];
   T0 = _ecl_car(v21);
   T1 = _ecl_cdr(v21);
   v20_degree_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_z_, T1);
  }
  v8_word_ = ECL_NIL;
  {
   cl_object v21;
   v21 = (v7_)->vector.self.t[27];
   T0 = _ecl_car(v21);
   T1 = _ecl_cdr(v21);
   v9_tmpv_ = (cl_env_copy->function=T0)->cfun.entry(3, v20_degree_, ecl_make_fixnum(0), T1);
  }
  v13_noresult_ = ECL_T;
  v19_j_ = v2_i_;
L27:;
  if (ecl_lower(v19_j_,ecl_make_fixnum(1))) { goto L33; }
  if (!(v13_noresult_==ECL_NIL)) { goto L31; }
  goto L32;
L33:;
L32:;
  goto L28;
L31:;
  {
   cl_fixnum v21;
   v21 = (ecl_fixnum(v19_j_))-(1);
   v18_orbj_ = ecl_aref_unsafe(v4_orbs_,v21);
  }
  v17_s_ = ECL_CONS_CDR(v18_orbj_);
  {
   cl_object v21;
   v21 = ECL_CONS_CAR(v18_orbj_);
   if (Null(v21)) { goto L43; }
   v16_p_ = _ecl_car(v21);
   goto L41;
L43:;
   v16_p_ = ecl_function_dispatch(cl_env_copy,VV[87])(0) /*  FIRST_ERROR */;
  }
L41:;
L48:;
  if (!(v13_noresult_==ECL_NIL)) { goto L50; }
  goto L49;
L50:;
  {
   cl_fixnum v21;
   {
    cl_fixnum v22;
    v22 = (ecl_fixnum(v16_p_))-(1);
    v21 = ecl_fixnum(ecl_aref_unsafe(v1_z_,v22));
   }
   {
    cl_fixnum v22;
    v22 = (v21)-(1);
    v15_entry_ = ecl_aref_unsafe(v17_s_,v22);
   }
  }
  if (!(ecl_lower(v15_entry_,ecl_make_fixnum(0)))) { goto L57; }
  if (!((v15_entry_)==(ecl_make_fixnum(-1)))) { goto L59; }
  v14 = ecl_make_fixnum(1);
  goto L46;
L59:;
  v13_noresult_ = ECL_NIL;
  goto L52;
L57:;
  {
   cl_fixnum v21;
   v21 = (ecl_fixnum(v15_entry_))-(1);
   v12_ee_ = ecl_aref_unsafe(v5_grpv_,v21);
  }
  L527_permgrp_times__(v9_tmpv_, v12_ee_, v1_z_, v7_);
  v11__g37_ = v9_tmpv_;
  v10__g38_ = v1_z_;
  v1_z_ = v11__g37_;
  v9_tmpv_ = v10__g38_;
  if (Null(v3_do_words_)) { goto L52; }
  {
   cl_object v21;
   v21 = (v7_)->vector.self.t[32];
   T0 = _ecl_car(v21);
   {
    cl_object v22;
    v22 = (v7_)->vector.self.t[31];
    T2 = _ecl_car(v22);
    T3 = _ecl_cdr(v22);
    T1 = (cl_env_copy->function=T2)->cfun.entry(3, v6_wordv_, v15_entry_, T3);
   }
   T2 = _ecl_cdr(v21);
   v8_word_ = (cl_env_copy->function=T0)->cfun.entry(3, T1, v8_word_, T2);
  }
  goto L52;
L52:;
  goto L48;
L49:;
  goto L35;
L46:;
  goto L35;
L35:;
  v19_j_ = ecl_plus(v19_j_,ecl_make_fixnum(-1));
  goto L27;
L28:;
  goto L26;
L26:;
  value0 = CONS(v1_z_,v8_word_);
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for PERMGRP;orbitInternal                 */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L534_permgrp_orbitinternal_(cl_object v1_gp_, cl_object v2_startlist_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_pos_;
  cl_object v5_orbitlist_;
  cl_object v6_newlist_;
  cl_object v7_j_;
  cl_object v8_worklist_;
  cl_object v9;
  cl_object v10_gen_;
  cl_object v11_gpset_;
  v4_pos_ = ecl_make_fixnum(0);
  v5_orbitlist_ = ECL_NIL;
  v6_newlist_ = ECL_NIL;
  v7_j_ = ECL_NIL;
  v8_worklist_ = ECL_NIL;
  v9 = ECL_NIL;
  v10_gen_ = ECL_NIL;
  v11_gpset_ = ECL_NIL;
  v5_orbitlist_ = ecl_list1(v2_startlist_);
  v4_pos_ = ecl_make_fixnum(1);
L14:;
  {
   bool v12;
   v12 = ecl_zerop(v4_pos_);
   {
    bool v13;
    v13 = ecl_make_bool(v12)==ECL_NIL;
    if (!(ecl_make_bool(v13)==ECL_NIL)) { goto L16; }
   }
  }
  goto L15;
L16:;
  v11_gpset_ = ECL_CONS_CAR(v1_gp_);
  v10_gen_ = ECL_NIL;
  v9 = v11_gpset_;
L22:;
  if (ECL_ATOM(v9)) { goto L30; }
  v10_gen_ = _ecl_car(v9);
  goto L28;
L30:;
  goto L23;
L28:;
  v6_newlist_ = ECL_NIL;
  {
   cl_object v12;
   v12 = (v3_)->vector.self.t[40];
   T0 = _ecl_car(v12);
   T1 = _ecl_cdr(v12);
   v8_worklist_ = (cl_env_copy->function=T0)->cfun.entry(3, v5_orbitlist_, v4_pos_, T1);
  }
  v7_j_ = ecl_make_fixnum(ecl_length(v8_worklist_));
L42:;
  if (!(ecl_lower(v7_j_,ecl_make_fixnum(1)))) { goto L46; }
  goto L43;
L46:;
  {
   cl_object v12;
   v12 = (v3_)->vector.self.t[42];
   T1 = _ecl_car(v12);
   {
    cl_object v13;
    v13 = (v3_)->vector.self.t[41];
    T3 = _ecl_car(v13);
    T4 = _ecl_cdr(v13);
    T2 = (cl_env_copy->function=T3)->cfun.entry(3, v8_worklist_, v7_j_, T4);
   }
   T3 = _ecl_cdr(v12);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, v10_gen_, T2, T3);
  }
  v6_newlist_ = CONS(T0,v6_newlist_);
  goto L48;
L48:;
  v7_j_ = ecl_plus(v7_j_,ecl_make_fixnum(-1));
  goto L42;
L43:;
  goto L41;
L41:;
  {
   cl_object v12;
   v12 = (v3_)->vector.self.t[43];
   T1 = _ecl_car(v12);
   T2 = _ecl_cdr(v12);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, v6_newlist_, v5_orbitlist_, T2);
  }
  if (!(T0==ECL_NIL)) { goto L34; }
  v5_orbitlist_ = CONS(v6_newlist_,v5_orbitlist_);
  v4_pos_ = ecl_plus(v4_pos_,ecl_make_fixnum(1));
  goto L34;
L34:;
  v9 = _ecl_cdr(v9);
  goto L22;
L23:;
  goto L21;
L21:;
  v4_pos_ = ecl_minus(v4_pos_,ecl_make_fixnum(1));
  goto L18;
L18:;
  goto L14;
L15:;
  goto L13;
L13:;
  value0 = cl_reverse(v5_orbitlist_);
  return value0;
 }
}
/*      function definition for PERMGRP;ranelt                        */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L535_permgrp_ranelt_(cl_object v1_group_, cl_object v2_word_, cl_object v3_maxloops_, cl_object v4_)
{
 cl_object T0, T1, T2, T3, T4;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5_numberofloops_;
  cl_object v6_words_;
  cl_object v7;
  cl_object v8_randomelement_;
  cl_object v9_randominteger_;
  cl_object v10;
  cl_object v11_do_words_;
  cl_object v12_numberofgenerators_;
  v5_numberofloops_ = ecl_make_fixnum(0);
  v6_words_ = ECL_NIL;
  v7 = ECL_NIL;
  v8_randomelement_ = ECL_NIL;
  v9_randominteger_ = ecl_make_fixnum(0);
  v10 = ECL_NIL;
  v11_do_words_ = ECL_NIL;
  v12_numberofgenerators_ = ecl_make_fixnum(0);
  v12_numberofgenerators_ = ecl_make_fixnum(ecl_length(v1_group_));
  T0 = cl_random(1, v12_numberofgenerators_);
  v9_randominteger_ = ecl_plus(ecl_make_fixnum(1),T0);
  {
   cl_object v13;
   v13 = (v4_)->vector.self.t[44];
   T0 = _ecl_car(v13);
   T1 = _ecl_cdr(v13);
   v8_randomelement_ = (cl_env_copy->function=T0)->cfun.entry(3, v1_group_, v9_randominteger_, T1);
  }
  v6_words_ = ECL_NIL;
  {
   bool v13;
   v13 = v2_word_==ECL_NIL;
   v11_do_words_ = ecl_make_bool(ecl_make_bool(v13)==ECL_NIL);
  }
  if (Null(v11_do_words_)) { goto L21; }
  {
   cl_object v13;
   v13 = (v4_)->vector.self.t[45];
   T0 = _ecl_car(v13);
   {
    cl_object v14;
    v10 = v9_randominteger_;
    v14 = v10;
    {
     bool v15;
     v15 = ecl_greatereq(v10,ecl_make_fixnum(0));
     if (!(ecl_make_bool(v15)==ECL_NIL)) { goto L29; }
    }
    T2 = ecl_function_dispatch(cl_env_copy,VV[99])(3, v10, VV[11], VV[12]) /*  coerce_failure_msg */;
    ecl_function_dispatch(cl_env_copy,VV[93])(1, T2) /*  error        */;
L29:;
    T1 = v14;
   }
   T2 = _ecl_cdr(v13);
   v6_words_ = (cl_env_copy->function=T0)->cfun.entry(3, v2_word_, T1, T2);
  }
L21:;
  if (!(ecl_greater(v3_maxloops_,ecl_make_fixnum(0)))) { goto L32; }
  T0 = cl_random(1, v3_maxloops_);
  v5_numberofloops_ = ecl_plus(ecl_make_fixnum(1),T0);
  goto L31;
L32:;
  v5_numberofloops_ = v3_maxloops_;
L31:;
L37:;
  {
   bool v13;
   v13 = ecl_greater(v5_numberofloops_,ecl_make_fixnum(0));
   if (!(ecl_make_bool(v13)==ECL_NIL)) { goto L39; }
  }
  goto L38;
L39:;
  T0 = cl_random(1, v12_numberofgenerators_);
  v9_randominteger_ = ecl_plus(ecl_make_fixnum(1),T0);
  {
   cl_object v13;
   v13 = (v4_)->vector.self.t[44];
   T1 = _ecl_car(v13);
   T2 = _ecl_cdr(v13);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, v1_group_, v9_randominteger_, T2);
  }
  v8_randomelement_ = L528_permgrp_times_(T0, v8_randomelement_, v4_);
  if (Null(v11_do_words_)) { goto L49; }
  {
   cl_object v13;
   v13 = (v4_)->vector.self.t[32];
   T0 = _ecl_car(v13);
   {
    cl_object v14;
    v14 = (v4_)->vector.self.t[45];
    T2 = _ecl_car(v14);
    {
     cl_object v15;
     v7 = v9_randominteger_;
     v15 = v7;
     {
      bool v16;
      v16 = ecl_greatereq(v7,ecl_make_fixnum(0));
      if (!(ecl_make_bool(v16)==ECL_NIL)) { goto L60; }
     }
     T4 = ecl_function_dispatch(cl_env_copy,VV[99])(3, v7, VV[11], VV[12]) /*  coerce_failure_msg */;
     ecl_function_dispatch(cl_env_copy,VV[93])(1, T4) /*  error       */;
L60:;
     T3 = v15;
    }
    T4 = _ecl_cdr(v14);
    T1 = (cl_env_copy->function=T2)->cfun.entry(3, v2_word_, T3, T4);
   }
   T2 = _ecl_cdr(v13);
   v6_words_ = (cl_env_copy->function=T0)->cfun.entry(3, T1, v6_words_, T2);
  }
L49:;
  v5_numberofloops_ = ecl_minus(v5_numberofloops_,ecl_make_fixnum(1));
  goto L41;
L41:;
  goto L37;
L38:;
  goto L36;
L36:;
  value0 = CONS(v8_randomelement_,v6_words_);
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for PERMGRP;pointList;%L;11               */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L536_permgrp_pointlist__l_11_(cl_object v1_group_, cl_object v2_)
{
 cl_object T0, T1, T2, T3, T4, T5;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3_res_;
  cl_object v4_p0_;
  cl_object v5;
  cl_object v6;
  cl_object v7_p_;
  cl_object v8_support_;
  cl_object v9;
  cl_object v10_perm_;
  v3_res_ = ECL_NIL;
  v4_p0_ = ECL_NIL;
  v5 = ECL_NIL;
  v6 = ECL_NIL;
  v7_p_ = ECL_NIL;
  v8_support_ = ECL_NIL;
  v9 = ECL_NIL;
  v10_perm_ = ECL_NIL;
  T0 = ECL_CONS_CDR(v1_group_);
  T1 = (T0)->vector.self.t[4];
  {
   bool v11;
   v11 = T1==ECL_NIL;
   if (!(ecl_make_bool(v11)==ECL_NIL)) { goto L10; }
  }
  T0 = ECL_CONS_CDR(v1_group_);
  value0 = (T0)->vector.self.t[4];
  cl_env_copy->nvalues = 1;
  return value0;
L10:;
  v8_support_ = ECL_NIL;
  v10_perm_ = ECL_NIL;
  v9 = ECL_CONS_CAR(v1_group_);
L15:;
  if (ECL_ATOM(v9)) { goto L23; }
  v10_perm_ = _ecl_car(v9);
  goto L21;
L23:;
  goto L16;
L21:;
  {
   cl_object v11;
   v11 = (v2_)->vector.self.t[49];
   T0 = _ecl_car(v11);
   {
    cl_object v12;
    v12 = (v2_)->vector.self.t[48];
    T2 = _ecl_car(v12);
    {
     cl_object v13;
     v13 = (v2_)->vector.self.t[47];
     T4 = _ecl_car(v13);
     T5 = _ecl_cdr(v13);
     T3 = (cl_env_copy->function=T4)->cfun.entry(2, v10_perm_, T5);
    }
    T4 = ECL_CONS_CAR(T3);
    T5 = _ecl_cdr(v12);
    T1 = (cl_env_copy->function=T2)->cfun.entry(2, T4, T5);
   }
   T2 = _ecl_cdr(v11);
   v8_support_ = (cl_env_copy->function=T0)->cfun.entry(3, T1, v8_support_, T2);
  }
  goto L27;
L27:;
  v9 = _ecl_cdr(v9);
  goto L15;
L16:;
  goto L14;
L14:;
  v3_res_ = ECL_NIL;
  if (!(v8_support_==ECL_NIL)) { goto L45; }
  value0 = v3_res_;
  cl_env_copy->nvalues = 1;
  return value0;
L45:;
  if (Null(v8_support_)) { goto L49; }
  v4_p0_ = _ecl_car(v8_support_);
  goto L48;
L49:;
  v4_p0_ = ecl_function_dispatch(cl_env_copy,VV[87])(0) /*  FIRST_ERROR */;
L48:;
  v3_res_ = ecl_list1(v4_p0_);
  v7_p_ = ECL_NIL;
  v6 = _ecl_cdr(v8_support_);
L54:;
  if (ECL_ATOM(v6)) { goto L62; }
  v7_p_ = _ecl_car(v6);
  goto L60;
L62:;
  goto L55;
L60:;
  {
   cl_object v11;
   v11 = (v2_)->vector.self.t[50];
   T0 = _ecl_car(v11);
   T1 = _ecl_cdr(v11);
   if (Null((cl_env_copy->function=T0)->cfun.entry(3, v7_p_, v4_p0_, T1))) { goto L69; }
  }
  v5 = ECL_SYM_VAL(cl_env_copy,VV[14]);
  goto L67;
L69:;
  v4_p0_ = v7_p_;
  v3_res_ = CONS(v7_p_,v3_res_);
  goto L66;
L67:;
  goto L66;
L66:;
  v6 = _ecl_cdr(v6);
  goto L54;
L55:;
  goto L53;
L53:;
  T0 = ECL_CONS_CDR(v1_group_);
  T1 = cl_nreverse(v3_res_);
  value0 = (T0)->vector.self.t[4]= T1;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for PERMGRP;pointList;%L;12               */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L537_permgrp_pointlist__l_12_(cl_object v1_group_, cl_object v2_)
{
 cl_object T0, T1, T2, T3;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3_support_;
  cl_object v4;
  cl_object v5_perm_;
  v3_support_ = ECL_NIL;
  v4 = ECL_NIL;
  v5_perm_ = ECL_NIL;
  T0 = ECL_CONS_CDR(v1_group_);
  T1 = (T0)->vector.self.t[4];
  {
   bool v6;
   v6 = T1==ECL_NIL;
   if (!(ecl_make_bool(v6)==ECL_NIL)) { goto L5; }
  }
  T0 = ECL_CONS_CDR(v1_group_);
  value0 = (T0)->vector.self.t[4];
  cl_env_copy->nvalues = 1;
  return value0;
L5:;
  {
   cl_object v6;
   v6 = (v2_)->vector.self.t[53];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   v3_support_ = (cl_env_copy->function=T0)->cfun.entry(1, T1);
  }
  v5_perm_ = ECL_NIL;
  v4 = ECL_CONS_CAR(v1_group_);
L12:;
  if (ECL_ATOM(v4)) { goto L20; }
  v5_perm_ = _ecl_car(v4);
  goto L18;
L20:;
  goto L13;
L18:;
  {
   cl_object v6;
   v6 = (v2_)->vector.self.t[55];
   T0 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v2_)->vector.self.t[54];
    T2 = _ecl_car(v7);
    T3 = _ecl_cdr(v7);
    T1 = (cl_env_copy->function=T2)->cfun.entry(2, v5_perm_, T3);
   }
   T2 = _ecl_cdr(v6);
   v3_support_ = (cl_env_copy->function=T0)->cfun.entry(3, v3_support_, T1, T2);
  }
  goto L24;
L24:;
  v4 = _ecl_cdr(v4);
  goto L12;
L13:;
  goto L11;
L11:;
  T0 = ECL_CONS_CDR(v1_group_);
  {
   cl_object v6;
   v6 = (v2_)->vector.self.t[56];
   T2 = _ecl_car(v6);
   T3 = _ecl_cdr(v6);
   T1 = (cl_env_copy->function=T2)->cfun.entry(2, v3_support_, T3);
  }
  value0 = (T0)->vector.self.t[4]= T1;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for PERMGRP;ls_to_lnni                    */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L538_permgrp_ls_to_lnni_(cl_object v1_ls_, cl_object v2_supp_, cl_object v3_)
{
 cl_object T0, T1, T2, T3;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  cl_object v5_pp_;
  cl_object v6;
  cl_object v7_rp2_;
  cl_object v8_ls2_;
  cl_object v9_p1_;
  cl_object v10_pel_;
  cl_object v11_flag_;
  cl_object v12;
  cl_object v13_p2_;
  cl_object v14_i_;
  cl_object v15;
  cl_object v16_p_;
  cl_object v17;
  v4 = ECL_NIL;
  v5_pp_ = ECL_NIL;
  v6 = ECL_NIL;
  v7_rp2_ = ECL_NIL;
  v8_ls2_ = ECL_NIL;
  v9_p1_ = ECL_NIL;
  v10_pel_ = ECL_NIL;
  v11_flag_ = ECL_NIL;
  v12 = ECL_NIL;
  v13_p2_ = ECL_NIL;
  v14_i_ = ECL_NIL;
  v15 = ECL_NIL;
  v16_p_ = ECL_NIL;
  v17 = ECL_NIL;
  if (!(v1_ls_==ECL_NIL)) { goto L16; }
  value0 = ECL_NIL;
  cl_env_copy->nvalues = 1;
  return value0;
L16:;
  v17 = ECL_NIL;
  v14_i_ = ecl_make_fixnum(1);
  v16_p_ = ECL_NIL;
  v15 = v1_ls_;
L22:;
  if (ECL_ATOM(v15)) { goto L32; }
  v16_p_ = _ecl_car(v15);
  goto L30;
L32:;
  goto L23;
L30:;
  T0 = CONS(v14_i_,v16_p_);
  v17 = CONS(T0,v17);
  goto L36;
L36:;
  {
   cl_object v18;
   v18 = _ecl_cdr(v15);
   v14_i_ = ecl_make_fixnum((ecl_fixnum(v14_i_))+1);
   v15 = v18;
  }
  goto L22;
L23:;
  v8_ls2_ = cl_nreverse(v17);
  goto L19;
L19:;
  {
   cl_object v18;
   v18 = (v3_)->vector.self.t[61];
   T0 = _ecl_car(v18);
   T1 = (VV[18]->symbol.gfdef);
   T2 = CONS(T1,v3_);
   T3 = _ecl_cdr(v18);
   v8_ls2_ = (cl_env_copy->function=T0)->cfun.entry(3, T2, v8_ls2_, T3);
  }
  if (Null(v8_ls2_)) { goto L53; }
  v10_pel_ = _ecl_car(v8_ls2_);
  goto L52;
L53:;
  v10_pel_ = ecl_function_dispatch(cl_env_copy,VV[87])(0) /*  FIRST_ERROR */;
L52:;
  v9_p1_ = ECL_CONS_CDR(v10_pel_);
  v8_ls2_ = _ecl_cdr(v8_ls2_);
  v7_rp2_ = ECL_NIL;
  v11_flag_ = ECL_T;
  v14_i_ = ecl_make_fixnum(1);
  v13_p2_ = ECL_NIL;
  v12 = v2_supp_;
L64:;
  if (ECL_ATOM(v12)) { goto L74; }
  v13_p2_ = _ecl_car(v12);
  if (!(v11_flag_==ECL_NIL)) { goto L72; }
  goto L73;
L74:;
L73:;
  goto L65;
L72:;
  {
   cl_object v18;
   v18 = (v3_)->vector.self.t[50];
   T0 = _ecl_car(v18);
   T1 = _ecl_cdr(v18);
   if (Null((cl_env_copy->function=T0)->cfun.entry(3, v9_p1_, v13_p2_, T1))) { goto L79; }
  }
  T0 = ECL_CONS_CAR(v10_pel_);
  T1 = cl_list(2, T0, v14_i_);
  v7_rp2_ = CONS(T1,v7_rp2_);
  if (!(v8_ls2_==ECL_NIL)) { goto L87; }
  v11_flag_ = ECL_NIL;
  goto L79;
L87:;
  if (Null(v8_ls2_)) { goto L92; }
  v10_pel_ = _ecl_car(v8_ls2_);
  goto L91;
L92:;
  v10_pel_ = ecl_function_dispatch(cl_env_copy,VV[87])(0) /*  FIRST_ERROR */;
L91:;
  v9_p1_ = ECL_CONS_CDR(v10_pel_);
  v8_ls2_ = _ecl_cdr(v8_ls2_);
  goto L79;
L79:;
  {
   cl_object v18;
   v18 = _ecl_cdr(v12);
   v14_i_ = ecl_make_fixnum((ecl_fixnum(v14_i_))+1);
   v12 = v18;
  }
  goto L64;
L65:;
  goto L63;
L63:;
  {
   cl_object v18;
   v18 = (v3_)->vector.self.t[65];
   T0 = _ecl_car(v18);
   T1 = (VV[17]->symbol.gfdef);
   T2 = CONS(T1,v3_);
   T3 = _ecl_cdr(v18);
   v7_rp2_ = (cl_env_copy->function=T0)->cfun.entry(3, T2, v7_rp2_, T3);
  }
  v6 = ECL_NIL;
  v5_pp_ = ECL_NIL;
  v4 = v7_rp2_;
L113:;
  if (ECL_ATOM(v4)) { goto L121; }
  v5_pp_ = _ecl_car(v4);
  goto L119;
L121:;
  goto L114;
L119:;
  {
   cl_object v18;
   v18 = (v3_)->vector.self.t[66];
   T1 = _ecl_car(v18);
   T2 = _ecl_cdr(v18);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, v5_pp_, T2);
  }
  v6 = CONS(T0,v6);
  goto L125;
L125:;
  v4 = _ecl_cdr(v4);
  goto L113;
L114:;
  value0 = cl_nreverse(v6);
  return value0;
 }
}