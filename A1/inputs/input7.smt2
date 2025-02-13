(set-logic AUFLIA)
(assert (exists ((a Int)) (forall ((b Int)) (exists ((c Int)) (forall ((d Int)) (> (+ a b) (* c d)))))))
(check-sat)

