(set-logic AUFLIA)
(assert (xor 
            (not 
                (exists ((a Int)) 

                    (forall ((b Int)) 
                        (exists ((c Int)) 
                            (forall ((d Int)) 
                                (exists ((e Int)) 
                                    (and (> (+ a b c) (* d e)) 
                                         (< e 0)))))))) 
            (forall ((f Int)) (> f -100))))
(check-sat)

