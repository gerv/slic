/******************************************************************************/
/*                                                               Date:08/2012 */
/*                             PRESENTATION                                   */
/*                                                                            */
/*      Copyright 2012 TCL Communication Technology Holdings Limited.         */
/*                                                                            */
/* This material is company confidential, cannot be reproduced in any form    */
/* without the written permission of TCL Communication Technology Holdings    */
/* Limited.                                                                   */
/*                                                                            */
/* -------------------------------------------------------------------------- */
/* Author:  He Zhang                                                          */
/* E-Mail:  He.Zhang@tcl-mobile.com                                           */
/* Role  :  GLUE                                                              */
/* Reference documents :  05_[ADR-09-001]Framework Dev Specification.pdf      */
/* -------------------------------------------------------------------------- */
/* Comments:                                                                  */
/* File    : vender/tct/source/system/tct_diag/nv_tracability.h               */
/* Labels  :                                                                  */
/* -------------------------------------------------------------------------- */
/* ========================================================================== */
/* Modifications on Features list / Changes Request / Problems Report         */
/* -------------------------------------------------------------------------- */
/* date    | author         | key                | comment (what, where, why) */
/* --------|----------------|--------------------|--------------------------- */
/* 12/09/21| He.Zhang       | FR-334604          | Adjust to fit new role     */
/* 12/09/21| Guobing.Miao   | FR-334604          | Create for nv backup       */
/*---------|----------------|--------------------|--------------------------- */
/******************************************************************************/

#ifndef NV_TRACABILITY_H
#define NV_TRACABILITY_H

typedef enum {
    NV_TRACA_IMEI_I,
    NV_TRACA_BD_ADDR_I,
    NV_TRACA_WIFI_ADDR_I,
    NV_TRACA_TEST_STATUS_I,
    NV_TRACA_DATA_START,
    REF_PCBA_I=NV_TRACA_DATA_START,
    SHORT_CODE_I,
    ICS_I ,
    SITE_FAC_PCBA_I ,
    LINE_FAC_PCBA_I ,
    DATE_PROD_PCBA_I ,
    SN_PCBA_I ,
    INDUS_REF_HANDSET_I ,
    INFO_PTM_I ,
    SITE_FAC_HANDSET_I ,
    LINE_FAC_HANDSET_I ,
    DATE_PROD_HANDSET_I ,
    SN_HANDSET_I ,
    INFO_PTS_MINI_I ,
    INFO_NAME_MINI_I ,
    INFO_TECH_MINI_I ,
    INFO_GOLDEN_FLAG_I ,
    INFO_GOLDEN_DATE_I ,
    INFO_ID_BAIE_HDTB_I ,
    INFO_DATE_PASS_HDTB_I ,
    INFO_PROD_BAIE_PARA_SYS_I ,
    INFO_STATUS_PARA_SYS_I ,
    INFO_NBRE_PASS_PARA_SYS_I ,
    INFO_DATE_PASS_PARA_SYS_I ,
    INFO_PROD_BAIE_PARA_SYS_2_I ,
    INFO_STATUS_PARA_SYS_2_I,
    INFO_NBRE_PASS_PARA_SYS_2_I ,
    INFO_DATE_PASS_PARA_SYS_2_I,
    INFO_PROD_BAIE_PARA_SYS_3_I,
    INFO_STATUS_PARA_SYS_3_I,
    INFO_NBRE_PASS_PARA_SYS_3_I ,
    INFO_DATE_PASS_PARA_SYS_3_I ,
    INFO_PROD_BAIE_BW_I ,
    INFO_STATUS_BW_I ,
    INFO_NBRE_PASS_BW_I,
    INFO_DATE_BAIE_BW_I ,
    INFO_PROD_BAIE_GPS_I ,
    INFO_STATUS_GPS_I,
    INFO_NBRE_PASS_GPS_I,
    INFO_DATE_BAIE_GPS_I,
    INFO_STATUS_MMI_TEST_I,
    INFO_PROD_BAIE_FINAL_I,
    INFO_STATUS_FINAL_I,
    INFO_NBRE_PASS_FINAL_I,
    INFO_DATE_BAIE_FINAL_I,
    INFO_PROD_BAIE_FINAL_2_I,
    INFO_STATUS_FINAL_2_I,
    INFO_NBRE_PASS_FINAL_2_I,
    INFO_DATE_BAIE_FINAL_2_I,
    INFO_ID_BAIE_HDT_I ,
    INFO_DATE_PASS_HDT_I ,
    INFO_COMM_REF_I ,
    INFO_PTS_APPLI_I ,
    INFO_NAME_APPLI_I ,
    INFO_NAME_PERSO1_I ,
    INFO_NAME_PERSO2_I ,
    INFO_NAME_PERSO3_I ,
    INFO_NAME_PERSO4_I ,
    INFO_SPARE_REGION_I,
    TRACABILITY_ITEM_TYPE_MAX
}tracability_item_type;

typedef struct{
    unsigned char        AKEY[16];
    unsigned char        AKEY_CHECKSUM[4];
    unsigned char        SPC[6];
    unsigned char        OTKSL[6];
    unsigned char        IMEI_2[15];                // stored imei 2
    unsigned char        SPARE[427];
    unsigned char        DEF_FLAG;        // definition flag 0x31
} ExtendZONE;

typedef struct {
    unsigned char name[4];
    unsigned char imei[15];
    unsigned char bd_addr[6];
    unsigned char wifi_addr[6];
    unsigned char test_status[4];

    unsigned char data[512];
    //New added to meet NPI requirement
    ExtendZONE  data_extend;  //475 length
    unsigned short checksum;
} tracability_region_struct_t;

#endif /* NV_TRACABILITY_H */
