(set-logic AUFLIA)
(declare-fun E (Int Int) Bool)
(assert (forall ((x Int) (y Int)) (E x y)))
(check-sat)
