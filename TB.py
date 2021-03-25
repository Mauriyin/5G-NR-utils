class TBCalculator:
    
    def __init__(self, mcs_table, mcs, numlayers, Nsh_sym, Nprb_mdrs, overhead,
                 total_prbs):

        self.mcs_table = mcs_table
        self.mcs = mcs
        self.numlayers = numlayers
        self.Nsh_sym = Nsh_sym
        self.Nprb_mdrs = Nprb_mdrs
        self.overhead = overhead
        self.total_prbs = total_prbs
        self.Nrb_sc = 12

        if self.mcs_table == '64QAM':
            """ For 64QAM"""
            self.Qm = [
                2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6,
                6, 6, 6, 6, 6, 6, 6, 6, 2, 4, 6
            ]
            self.R = [
                120, 157, 193, 251, 308, 379, 449, 526, 602, 679, 340, 378,
                434, 490, 553, 616, 658, 438, 466, 517, 567, 616, 666, 719,
                772, 822, 873, 910, 948
            ]
            # Table 5.2.2.1-2: 4-bit CQI Table
            self.cqi2mcs = [0, 0, 0, 2, 4, 6, 8, 11, 13, 15, 18, 20, 22, 24, 26, 28]

        elif self.mcs_table == '256QAM':
            """ For 256QAM"""
            self.Qm = [
                2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 8,
                8, 8, 8, 8, 8, 8, 8, 2, 4, 6, 8
            ]
            self.R = [
                120, 193, 308, 449, 602, 378, 434, 490, 553, 616, 658, 466,
                517, 567, 616, 666, 719, 772, 822, 873, 682.5, 711, 754, 797,
                841, 885, 916.5, 948
            ]
            # Table 5.2.2.1-2: 4-bit CQI Table 2
            self.cqi2mcs = [0, 0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27]
        else:
            raise ValueError("Incorrect Value entered by user!")

    def TB_calc(self):

        mcs_index = self.mcs
        modulation_order = self.Qm[mcs_index]
        code_rate = self.R[mcs_index] / 1024.00000
        # print("The code rate used is",code_rate ,"and modulation order is", modulation_order)
        nre_prb = (self.Nrb_sc * self.Nsh_sym) - self.Nprb_mdrs - self.overhead
        N_re = min(156, nre_prb) * self.total_prbs
        N_info = N_re * code_rate * modulation_order * self.numlayers
        # print("Intermediate number of information bits are", N_info)

        if N_info <= 3824:
            n = max(3, math.floor(math.log(N_info, 2)) - 6)
            N_info_quant_1 = max(
                24,
                math.pow(2, n) * math.floor(N_info / math.pow(2, n)))
            # print("\nquantized intermediate number of information bits : ",
            #       N_info_quant_1,
            #       "\nFor TBS please refer to table 5.1.3.2-2 in 38.214")
            return N_info_quant_1
        else:
            n = math.floor(math.log(N_info - 24, 2)) - 5
            N_info_quant = max(
                3840,
                math.pow(2, n) * round((N_info - 24) / math.pow(2, n)))
            #print ("quantized intermediate number of information bits :\n",N_info_quant )

        if code_rate <= 0.25:
            C = math.ceil((N_info_quant + 24) / 3816)
            TBS = 8 * C * math.ceil((N_info_quant + 24) / (8 * C)) - 24
            # print("Code rate > 1/4 and TB size is : %r\n") %TBS
        else:
            if N_info_quant > 8424:
                C = math.ceil((N_info_quant + 24) / 8424)
                TBS = 8 * C * math.ceil((N_info_quant + 24) / (8 * C)) - 24
                avg_tpt = ((TBS * 160 / 80) * 1000)
                # print("As N_info_quant > 8424 and Code rate > 1/4, TB size is :\n",TBS)
                # print("Average throughput : %r bps") %avg_tpt
            else:
                TBS = 8 * math.ceil((N_info_quant + 24) / 8) - 24
                avg_tpt = ((TBS * 160 / 80) * 1000)
                # print("As N_info_quant < 8424 and Code rate > 1/4,TB size is :\n",TBS)

        return TBS

    def cal_by_cqi(self, cqi, rb_num):
        self.mcs = self.cqi2mcs[cqi]
        self.total_prbs = rb_num
        TBS = self.TB_calc()
        return TBS
