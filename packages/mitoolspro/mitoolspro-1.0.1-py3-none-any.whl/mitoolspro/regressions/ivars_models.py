from typing import List, Optional

from linearmodels import IV2SLS, IVGMM, IVGMMCUE, IVLIML
from pandas import DataFrame

from mitoolspro.exceptions import ArgumentValueError
from mitoolspro.regressions.base_models import BaseRegressionModel


class IV2SLSModel(BaseRegressionModel):
    def __init__(
        self,
        data: DataFrame,
        formula: Optional[str] = None,
        dependent_variable: Optional[str] = None,
        independent_variables: Optional[List[str]] = None,
        control_variables: Optional[List[str]] = None,
        endogenous_variables: Optional[List[str]] = None,
        instrument_variables: Optional[List[str]] = None,
        *args,
        **kwargs,
    ):
        super().__init__(
            data=data,
            formula=formula,
            dependent_variable=dependent_variable,
            independent_variables=independent_variables,
            control_variables=control_variables,
            *args,
            **kwargs,
        )
        self.endogenous_variables = endogenous_variables or []
        self.instrument_variables = instrument_variables or []

        self.model_name = "IV2SLS"

    def fit(self, add_constant: bool = True, *args, **kwargs):
        if self.formula is not None:
            self.model = IV2SLS.from_formula(
                formula=self.formula, data=self.data, *self.args, **self.kwargs
            )
        else:
            endog = self.data[self.dependent_variable]
            exog_vars = self.independent_variables + self.control_variables
            exog_vars = [
                var for var in exog_vars if var not in self.endogenous_variables
            ]
            exog = self.data[exog_vars]
            if add_constant:
                if "const" not in exog_vars:
                    exog = exog.assign(const=1)
                    exog = exog[["const"] + exog_vars]
            endog_reg = None
            if self.endogenous_variables:
                endog_reg = self.data[self.endogenous_variables]
            instr = None
            if self.instrument_variables:
                instr = self.data[self.instrument_variables]
            self.model = IV2SLS(
                endog, exog, endog_reg, instr, *self.args, **self.kwargs
            )
        self.results = self.model.fit(*args, **kwargs)
        self.fitted = True
        return self.results

    def predict(self, new_data: Optional[DataFrame] = None):
        if not self.fitted:
            raise ArgumentValueError("Model not fitted yet")
        if new_data is None:
            return self.results.predict()
        if self.formula is not None:
            return self.results.predict(new_data)
        else:
            exog_vars = self.independent_variables + self.control_variables
            exog_vars = [
                var for var in exog_vars if var not in self.endogenous_variables
            ]
            missing_exog = [var for var in exog_vars if var not in new_data.columns]
            if missing_exog:
                raise ArgumentValueError(
                    f"new_data is missing required exogenous variables: {missing_exog}"
                )
            missing_endog = [
                var for var in self.endogenous_variables if var not in new_data.columns
            ]
            if missing_endog:
                raise ArgumentValueError(
                    f"new_data is missing required endogenous variables: {missing_endog}"
                )
            if self.results.model.has_constant and "const" not in new_data.columns:
                new_data = new_data.assign(const=1)

            exog = new_data[exog_vars]
            if self.results.model.has_constant and "const" not in exog.columns:
                exog = exog.assign(const=1)
                exog = exog[["const"] + exog_vars]

            endog = (
                new_data[self.endogenous_variables]
                if self.endogenous_variables
                else None
            )

            return self.results.predict(exog=exog, endog=endog)


class IVGMMModel(BaseRegressionModel):
    def __init__(
        self,
        data: DataFrame,
        formula: Optional[str] = None,
        dependent_variable: Optional[str] = None,
        independent_variables: Optional[List[str]] = None,
        control_variables: Optional[List[str]] = None,
        endogenous_variables: Optional[List[str]] = None,
        instrument_variables: Optional[List[str]] = None,
        *args,
        **kwargs,
    ):
        super().__init__(
            data=data,
            formula=formula,
            dependent_variable=dependent_variable,
            independent_variables=independent_variables,
            control_variables=control_variables,
            *args,
            **kwargs,
        )
        self.endogenous_variables = endogenous_variables or []
        self.instrument_variables = instrument_variables or []

        self.model_name = "IVGMM"

    def fit(self, add_constant: bool = True, *args, **kwargs):
        if self.formula is not None:
            self.model = IVGMM.from_formula(
                formula=self.formula, data=self.data, *self.args, **self.kwargs
            )
        else:
            endog = self.data[self.dependent_variable]
            exog_vars = self.independent_variables + self.control_variables
            exog_vars = [
                var for var in exog_vars if var not in self.endogenous_variables
            ]
            exog = self.data[exog_vars]
            if add_constant:
                if "const" not in exog_vars:
                    exog = exog.assign(const=1)
                    exog = exog[["const"] + exog_vars]
            endog_reg = None
            if self.endogenous_variables:
                endog_reg = self.data[self.endogenous_variables]
            instr = None
            if self.instrument_variables:
                instr = self.data[self.instrument_variables]
            self.model = IVGMM(endog, exog, endog_reg, instr, *self.args, **self.kwargs)
        self.results = self.model.fit(*args, **kwargs)
        self.fitted = True
        return self.results

    def predict(self, new_data: Optional[DataFrame] = None):
        if not self.fitted:
            raise ArgumentValueError("Model not fitted yet")
        if new_data is None:
            return self.results.predict()
        if self.formula is not None:
            return self.results.predict(new_data)
        else:
            exog_vars = self.independent_variables + self.control_variables
            exog_vars = [
                var for var in exog_vars if var not in self.endogenous_variables
            ]
            missing_exog = [var for var in exog_vars if var not in new_data.columns]
            if missing_exog:
                raise ArgumentValueError(
                    f"new_data is missing required exogenous variables: {missing_exog}"
                )
            missing_endog = [
                var for var in self.endogenous_variables if var not in new_data.columns
            ]
            if missing_endog:
                raise ArgumentValueError(
                    f"new_data is missing required endogenous variables: {missing_endog}"
                )
            if self.results.model.has_constant and "const" not in new_data.columns:
                new_data = new_data.assign(const=1)

            exog = new_data[exog_vars]
            if self.results.model.has_constant and "const" not in exog.columns:
                exog = exog.assign(const=1)
                exog = exog[["const"] + exog_vars]

            endog = (
                new_data[self.endogenous_variables]
                if self.endogenous_variables
                else None
            )

            return self.results.predict(exog=exog, endog=endog)


class IVGMMCUEModel(BaseRegressionModel):
    def __init__(
        self,
        data: DataFrame,
        formula: Optional[str] = None,
        dependent_variable: Optional[str] = None,
        independent_variables: Optional[List[str]] = None,
        control_variables: Optional[List[str]] = None,
        endogenous_variables: Optional[List[str]] = None,
        instrument_variables: Optional[List[str]] = None,
        *args,
        **kwargs,
    ):
        super().__init__(
            data=data,
            formula=formula,
            dependent_variable=dependent_variable,
            independent_variables=independent_variables,
            control_variables=control_variables,
            *args,
            **kwargs,
        )
        self.endogenous_variables = endogenous_variables or []
        self.instrument_variables = instrument_variables or []

        self.model_name = "IVGMMCUE"

    def fit(self, add_constant: bool = True, *args, **kwargs):
        if self.formula is not None:
            self.model = IVGMMCUE.from_formula(
                formula=self.formula, data=self.data, *self.args, **self.kwargs
            )
        else:
            endog = self.data[self.dependent_variable]
            exog_vars = self.independent_variables + self.control_variables
            exog_vars = [
                var for var in exog_vars if var not in self.endogenous_variables
            ]
            exog = self.data[exog_vars]
            if add_constant:
                if "const" not in exog_vars:
                    exog = exog.assign(const=1)
                    exog = exog[["const"] + exog_vars]
            endog_reg = None
            if self.endogenous_variables:
                endog_reg = self.data[self.endogenous_variables]
            instr = None
            if self.instrument_variables:
                instr = self.data[self.instrument_variables]
            self.model = IVGMMCUE(
                endog, exog, endog_reg, instr, *self.args, **self.kwargs
            )
        self.results = self.model.fit(*args, **kwargs)
        self.fitted = True
        return self.results

    def predict(self, new_data: Optional[DataFrame] = None):
        if not self.fitted:
            raise ArgumentValueError("Model not fitted yet")
        if new_data is None:
            return self.results.predict()
        if self.formula is not None:
            return self.results.predict(new_data)
        else:
            exog_vars = self.independent_variables + self.control_variables
            exog_vars = [
                var for var in exog_vars if var not in self.endogenous_variables
            ]
            missing_exog = [var for var in exog_vars if var not in new_data.columns]
            if missing_exog:
                raise ArgumentValueError(
                    f"new_data is missing required exogenous variables: {missing_exog}"
                )
            missing_endog = [
                var for var in self.endogenous_variables if var not in new_data.columns
            ]
            if missing_endog:
                raise ArgumentValueError(
                    f"new_data is missing required endogenous variables: {missing_endog}"
                )
            if self.results.model.has_constant and "const" not in new_data.columns:
                new_data = new_data.assign(const=1)

            exog = new_data[exog_vars]
            if self.results.model.has_constant and "const" not in exog.columns:
                exog = exog.assign(const=1)
                exog = exog[["const"] + exog_vars]

            endog = (
                new_data[self.endogenous_variables]
                if self.endogenous_variables
                else None
            )

            return self.results.predict(exog=exog, endog=endog)


class IVLIMLModel(BaseRegressionModel):
    def __init__(
        self,
        data: DataFrame,
        formula: Optional[str] = None,
        dependent_variable: Optional[str] = None,
        independent_variables: Optional[List[str]] = None,
        control_variables: Optional[List[str]] = None,
        endogenous_variables: Optional[List[str]] = None,
        instrument_variables: Optional[List[str]] = None,
        *args,
        **kwargs,
    ):
        super().__init__(
            data=data,
            formula=formula,
            dependent_variable=dependent_variable,
            independent_variables=independent_variables,
            control_variables=control_variables,
            *args,
            **kwargs,
        )
        self.endogenous_variables = endogenous_variables or []
        self.instrument_variables = instrument_variables or []

        self.model_name = "IVLIML"

    def fit(self, add_constant: bool = True, *args, **kwargs):
        if self.formula is not None:
            self.model = IVLIML.from_formula(
                formula=self.formula, data=self.data, *self.args, **self.kwargs
            )
        else:
            endog = self.data[self.dependent_variable]
            exog_vars = self.independent_variables + self.control_variables
            exog_vars = [
                var for var in exog_vars if var not in self.endogenous_variables
            ]
            exog = self.data[exog_vars]
            if add_constant:
                if "const" not in exog_vars:
                    exog = exog.assign(const=1)
                    exog = exog[["const"] + exog_vars]
            endog_reg = None
            if self.endogenous_variables:
                endog_reg = self.data[self.endogenous_variables]
            instr = None
            if self.instrument_variables:
                instr = self.data[self.instrument_variables]
            self.model = IVLIML(
                endog, exog, endog_reg, instr, *self.args, **self.kwargs
            )
        self.results = self.model.fit(*args, **kwargs)
        self.fitted = True
        return self.results

    def predict(self, new_data: Optional[DataFrame] = None):
        if not self.fitted:
            raise ArgumentValueError("Model not fitted yet")
        if new_data is None:
            return self.results.predict()
        if self.formula is not None:
            return self.results.predict(new_data)
        else:
            exog_vars = self.independent_variables + self.control_variables
            exog_vars = [
                var for var in exog_vars if var not in self.endogenous_variables
            ]
            missing_exog = [var for var in exog_vars if var not in new_data.columns]
            if missing_exog:
                raise ArgumentValueError(
                    f"new_data is missing required exogenous variables: {missing_exog}"
                )
            missing_endog = [
                var for var in self.endogenous_variables if var not in new_data.columns
            ]
            if missing_endog:
                raise ArgumentValueError(
                    f"new_data is missing required endogenous variables: {missing_endog}"
                )
            if self.results.model.has_constant and "const" not in new_data.columns:
                new_data = new_data.assign(const=1)

            exog = new_data[exog_vars]
            if self.results.model.has_constant and "const" not in exog.columns:
                exog = exog.assign(const=1)
                exog = exog[["const"] + exog_vars]

            endog = (
                new_data[self.endogenous_variables]
                if self.endogenous_variables
                else None
            )

            return self.results.predict(exog=exog, endog=endog)
