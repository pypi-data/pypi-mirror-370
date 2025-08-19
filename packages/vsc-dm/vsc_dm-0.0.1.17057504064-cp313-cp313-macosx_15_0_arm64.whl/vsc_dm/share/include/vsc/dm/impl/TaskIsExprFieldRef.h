/*
 * Copyright 2019-2023 Matthew Ballance and contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#pragma once
#include "vsc/dm/impl/VisitorBase.h"

namespace vsc {
namespace dm {

class TaskIsExprFieldRef : public virtual VisitorBase {
public:

    TaskIsExprFieldRef() : m_field(0) { }

    virtual ~TaskIsExprFieldRef() { }

    IModelField *check(IModelExpr *e) {
        m_field = 0;
        e->accept(m_this);
        return m_field;
    }

	virtual void visitModelExprFieldRef(IModelExprFieldRef *e) override {
        m_field = e->field();
    }

private:
    IModelField                 *m_field;

};

}
}
