/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Op Declarations                                                            *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|* From: TritonInstrumentOps.td                                               *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace mlir {
namespace triton {
namespace instrument {
/// assert the condition within the current thread
/// Assert that the condition is true given all the values are available in the current thread.
///     If the condition is false, the message is printed, and the program is aborted.
///     If check_any is true, any of the values in the condition must be true. Otherwise, all the
///     values in the condition must be true.
class ExperimentalAssertInThreadOp;
} // namespace instrument
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace instrument {
/// check if there are outstanding reads from a buffer guarded by a mbar
/// Check if there are outstanding reads from a buffer guarded by a mbar.
class ExperimentalCheckOutstandingReadsOp;
} // namespace instrument
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace instrument {
/// check if there are outstanding writes to a buffer guarded by a mbar
/// Check if there are outstanding writes to a buffer guarded by a mbar.
class ExperimentalCheckOutstandingWritesOp;
} // namespace instrument
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace instrument {
/// Check if the buffer has an outstanding write commit.
/// Check if the buffer has an outstanding write commit.
class ExperimentalCheckWriteCommitOp;
} // namespace instrument
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace instrument {
/// clear the read state for buffers being guarded by an mbar
/// Clear the read state for buffers being guarded by an mbar.
class ExperimentalClearReadBarrierOp;
} // namespace instrument
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace instrument {
/// clear the write state for buffers being guarded by an mbar
/// Clear the write state for buffers being guarded by an mbar.
class ExperimentalClearWriteBarrierOp;
} // namespace instrument
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace instrument {
/// Clear all the write commits more distant than `outstandingNum.
/// Clear all the write commits more distant than `outstandingNum` from the current thread.
class ExperimentalClearWriteCommitsOp;
} // namespace instrument
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace instrument {
/// Commit all the staged writes for all the buffers.
/// Commit all the staged writes for all the buffers.
class ExperimentalCommitWritesOp;
} // namespace instrument
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace instrument {
/// mark a buffer as being read from using mbar as a guard
/// Mark a buffer as being read from using mbar as a guard.
class ExperimentalMarkAsReadOp;
} // namespace instrument
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace instrument {
/// mark a buffer as being written to using mbar as a guard
/// Mark a buffer as being written to using mbar as a guard.
class ExperimentalMarkAsWriteOp;
} // namespace instrument
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace instrument {
/// definte an array of pointers to shared memory buffers
/// Create a tensor of pointers to shared memory buffers.
class ExperimentalSharedBufferPointersOp;
} // namespace instrument
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace instrument {
/// Preapre to an async copy of a buffer. Staged until commit_group is called.
/// Preapre to an async copy of a buffer. Staged until commit_group is called. The implementation will write `-1` to the
///     `write_commits` tensor under the indices corresponding to the buffer.
class ExperimentalStageWriteForCommitOp;
} // namespace instrument
} // namespace triton
} // namespace mlir
#ifdef GET_OP_CLASSES
#undef GET_OP_CLASSES

namespace mlir {
namespace triton {
namespace instrument {

//===----------------------------------------------------------------------===//
// ::mlir::triton::instrument::ExperimentalAssertInThreadOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class ExperimentalAssertInThreadOpGenericAdaptorBase {
public:
  struct Properties {
    using check_anyTy = ::mlir::BoolAttr;
    check_anyTy check_any;

    auto getCheckAny() const {
      auto &propStorage = this->check_any;
      return ::llvm::cast<::mlir::BoolAttr>(propStorage);
    }
    void setCheckAny(const ::mlir::BoolAttr &propValue) {
      this->check_any = propValue;
    }
    using messageTy = ::mlir::StringAttr;
    messageTy message;

    auto getMessage() const {
      auto &propStorage = this->message;
      return ::llvm::cast<::mlir::StringAttr>(propStorage);
    }
    void setMessage(const ::mlir::StringAttr &propValue) {
      this->message = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.check_any == this->check_any &&
        rhs.message == this->message &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  ExperimentalAssertInThreadOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("tti.experimental_assert_in_thread", odsAttrs.getContext());
  }

  ExperimentalAssertInThreadOpGenericAdaptorBase(ExperimentalAssertInThreadOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
    return {index, 1};
  }

  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::StringAttr getMessageAttr() {
    auto attr = ::llvm::cast<::mlir::StringAttr>(getProperties().message);
    return attr;
  }

  ::llvm::StringRef getMessage();
  ::mlir::BoolAttr getCheckAnyAttr() {
    auto attr = ::llvm::cast<::mlir::BoolAttr>(getProperties().check_any);
    return attr;
  }

  bool getCheckAny();
};
} // namespace detail
template <typename RangeT>
class ExperimentalAssertInThreadOpGenericAdaptor : public detail::ExperimentalAssertInThreadOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::ExperimentalAssertInThreadOpGenericAdaptorBase;
  static constexpr int odsIndex_condition = 0;
public:
  ExperimentalAssertInThreadOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  ExperimentalAssertInThreadOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : ExperimentalAssertInThreadOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  ExperimentalAssertInThreadOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : ExperimentalAssertInThreadOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  ExperimentalAssertInThreadOpGenericAdaptor(RangeT values, const ExperimentalAssertInThreadOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = ExperimentalAssertInThreadOp, typename = std::enable_if_t<std::is_same_v<LateInst, ExperimentalAssertInThreadOp>>>
  ExperimentalAssertInThreadOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getCondition() {
    return (*getODSOperands(0).begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class ExperimentalAssertInThreadOpAdaptor : public ExperimentalAssertInThreadOpGenericAdaptor<::mlir::ValueRange> {
public:
  using ExperimentalAssertInThreadOpGenericAdaptor::ExperimentalAssertInThreadOpGenericAdaptor;
  ExperimentalAssertInThreadOpAdaptor(ExperimentalAssertInThreadOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class ExperimentalAssertInThreadOp : public ::mlir::Op<ExperimentalAssertInThreadOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::OneOperand, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ExperimentalAssertInThreadOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = ExperimentalAssertInThreadOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_condition = 0;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("check_any"), ::llvm::StringRef("message")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getCheckAnyAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getCheckAnyAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr getMessageAttrName() {
    return getAttributeNameForIndex(1);
  }

  static ::mlir::StringAttr getMessageAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 1);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("tti.experimental_assert_in_thread");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::TensorType> getCondition() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::TensorType>>(*getODSOperands(0).begin());
  }

  ::mlir::OpOperand &getConditionMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::StringAttr getMessageAttr() {
    return ::llvm::cast<::mlir::StringAttr>(getProperties().message);
  }

  ::llvm::StringRef getMessage();
  ::mlir::BoolAttr getCheckAnyAttr() {
    return ::llvm::cast<::mlir::BoolAttr>(getProperties().check_any);
  }

  bool getCheckAny();
  void setMessageAttr(::mlir::StringAttr attr) {
    getProperties().message = attr;
  }

  void setMessage(::llvm::StringRef attrValue);
  void setCheckAnyAttr(::mlir::BoolAttr attr) {
    getProperties().check_any = attr;
  }

  void setCheckAny(bool attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value condition, ::mlir::StringAttr message, ::mlir::BoolAttr check_any);
  static ExperimentalAssertInThreadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value condition, ::mlir::StringAttr message, ::mlir::BoolAttr check_any);
  static ExperimentalAssertInThreadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value condition, ::mlir::StringAttr message, ::mlir::BoolAttr check_any);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value condition, ::mlir::StringAttr message, ::mlir::BoolAttr check_any);
  static ExperimentalAssertInThreadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value condition, ::mlir::StringAttr message, ::mlir::BoolAttr check_any);
  static ExperimentalAssertInThreadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value condition, ::mlir::StringAttr message, ::mlir::BoolAttr check_any);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value condition, ::llvm::StringRef message, bool check_any);
  static ExperimentalAssertInThreadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value condition, ::llvm::StringRef message, bool check_any);
  static ExperimentalAssertInThreadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value condition, ::llvm::StringRef message, bool check_any);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value condition, ::llvm::StringRef message, bool check_any);
  static ExperimentalAssertInThreadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value condition, ::llvm::StringRef message, bool check_any);
  static ExperimentalAssertInThreadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value condition, ::llvm::StringRef message, bool check_any);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalAssertInThreadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalAssertInThreadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalAssertInThreadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalAssertInThreadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 2 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace instrument
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::instrument::ExperimentalAssertInThreadOp)

namespace mlir {
namespace triton {
namespace instrument {

//===----------------------------------------------------------------------===//
// ::mlir::triton::instrument::ExperimentalCheckOutstandingReadsOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class ExperimentalCheckOutstandingReadsOpGenericAdaptorBase {
public:
  struct Properties {
    using readBarsTypeTy = ::mlir::TypeAttr;
    readBarsTypeTy readBarsType;

    auto getReadBarsType() const {
      auto &propStorage = this->readBarsType;
      return ::llvm::cast<::mlir::TypeAttr>(propStorage);
    }
    void setReadBarsType(const ::mlir::TypeAttr &propValue) {
      this->readBarsType = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.readBarsType == this->readBarsType &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  ExperimentalCheckOutstandingReadsOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("tti.experimental_check_outstanding_reads", odsAttrs.getContext());
  }

  ExperimentalCheckOutstandingReadsOpGenericAdaptorBase(ExperimentalCheckOutstandingReadsOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::TypeAttr getReadBarsTypeAttr() {
    auto attr = ::llvm::cast<::mlir::TypeAttr>(getProperties().readBarsType);
    return attr;
  }

  ::mlir::Type getReadBarsType();
};
} // namespace detail
template <typename RangeT>
class ExperimentalCheckOutstandingReadsOpGenericAdaptor : public detail::ExperimentalCheckOutstandingReadsOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::ExperimentalCheckOutstandingReadsOpGenericAdaptorBase;
  static constexpr int odsIndex_buf = 0;
  static constexpr int odsIndex_buffers = 1;
  static constexpr int odsIndex_readBars = 2;
  static constexpr int odsIndex_pred = 3;
public:
  ExperimentalCheckOutstandingReadsOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  ExperimentalCheckOutstandingReadsOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : ExperimentalCheckOutstandingReadsOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  ExperimentalCheckOutstandingReadsOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : ExperimentalCheckOutstandingReadsOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  ExperimentalCheckOutstandingReadsOpGenericAdaptor(RangeT values, const ExperimentalCheckOutstandingReadsOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = ExperimentalCheckOutstandingReadsOp, typename = std::enable_if_t<std::is_same_v<LateInst, ExperimentalCheckOutstandingReadsOp>>>
  ExperimentalCheckOutstandingReadsOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getBuf() {
    return (*getODSOperands(0).begin());
  }

  ValueT getBuffers() {
    return (*getODSOperands(1).begin());
  }

  ValueT getReadBars() {
    return (*getODSOperands(2).begin());
  }

  ValueT getPred() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class ExperimentalCheckOutstandingReadsOpAdaptor : public ExperimentalCheckOutstandingReadsOpGenericAdaptor<::mlir::ValueRange> {
public:
  using ExperimentalCheckOutstandingReadsOpGenericAdaptor::ExperimentalCheckOutstandingReadsOpGenericAdaptor;
  ExperimentalCheckOutstandingReadsOpAdaptor(ExperimentalCheckOutstandingReadsOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class ExperimentalCheckOutstandingReadsOp : public ::mlir::Op<ExperimentalCheckOutstandingReadsOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<3>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ExperimentalCheckOutstandingReadsOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = ExperimentalCheckOutstandingReadsOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_buf = 0;
  static constexpr int odsIndex_buffers = 1;
  static constexpr int odsIndex_readBars = 2;
  static constexpr int odsIndex_pred = 3;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("readBarsType")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getReadBarsTypeAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getReadBarsTypeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("tti.experimental_check_outstanding_reads");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::triton::gpu::MemDescType> getBuf() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::MemDescType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getBuffers() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::Type> getReadBars() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::Type>>(*getODSOperands(2).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getPred() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ::mlir::TypedValue<::mlir::IntegerType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*operands.begin());
  }

  ::mlir::OpOperand &getBufMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBuffersMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getReadBarsMutable() {
    auto range = getODSOperandIndexAndLength(2);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getPredMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::TypeAttr getReadBarsTypeAttr() {
    return ::llvm::cast<::mlir::TypeAttr>(getProperties().readBarsType);
  }

  ::mlir::Type getReadBarsType();
  void setReadBarsTypeAttr(::mlir::TypeAttr attr) {
    getProperties().readBarsType = attr;
  }

  void setReadBarsType(::mlir::Type attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingReadsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingReadsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingReadsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingReadsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingReadsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingReadsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingReadsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingReadsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalCheckOutstandingReadsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalCheckOutstandingReadsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalCheckOutstandingReadsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalCheckOutstandingReadsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace instrument
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::instrument::ExperimentalCheckOutstandingReadsOp)

namespace mlir {
namespace triton {
namespace instrument {

//===----------------------------------------------------------------------===//
// ::mlir::triton::instrument::ExperimentalCheckOutstandingWritesOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class ExperimentalCheckOutstandingWritesOpGenericAdaptorBase {
public:
  struct Properties {
    using writeBarsTypeTy = ::mlir::TypeAttr;
    writeBarsTypeTy writeBarsType;

    auto getWriteBarsType() const {
      auto &propStorage = this->writeBarsType;
      return ::llvm::cast<::mlir::TypeAttr>(propStorage);
    }
    void setWriteBarsType(const ::mlir::TypeAttr &propValue) {
      this->writeBarsType = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.writeBarsType == this->writeBarsType &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  ExperimentalCheckOutstandingWritesOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("tti.experimental_check_outstanding_writes", odsAttrs.getContext());
  }

  ExperimentalCheckOutstandingWritesOpGenericAdaptorBase(ExperimentalCheckOutstandingWritesOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::TypeAttr getWriteBarsTypeAttr() {
    auto attr = ::llvm::cast<::mlir::TypeAttr>(getProperties().writeBarsType);
    return attr;
  }

  ::mlir::Type getWriteBarsType();
};
} // namespace detail
template <typename RangeT>
class ExperimentalCheckOutstandingWritesOpGenericAdaptor : public detail::ExperimentalCheckOutstandingWritesOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::ExperimentalCheckOutstandingWritesOpGenericAdaptorBase;
  static constexpr int odsIndex_buf = 0;
  static constexpr int odsIndex_buffers = 1;
  static constexpr int odsIndex_writeBars = 2;
  static constexpr int odsIndex_pred = 3;
public:
  ExperimentalCheckOutstandingWritesOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  ExperimentalCheckOutstandingWritesOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : ExperimentalCheckOutstandingWritesOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  ExperimentalCheckOutstandingWritesOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : ExperimentalCheckOutstandingWritesOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  ExperimentalCheckOutstandingWritesOpGenericAdaptor(RangeT values, const ExperimentalCheckOutstandingWritesOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = ExperimentalCheckOutstandingWritesOp, typename = std::enable_if_t<std::is_same_v<LateInst, ExperimentalCheckOutstandingWritesOp>>>
  ExperimentalCheckOutstandingWritesOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getBuf() {
    return (*getODSOperands(0).begin());
  }

  ValueT getBuffers() {
    return (*getODSOperands(1).begin());
  }

  ValueT getWriteBars() {
    return (*getODSOperands(2).begin());
  }

  ValueT getPred() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class ExperimentalCheckOutstandingWritesOpAdaptor : public ExperimentalCheckOutstandingWritesOpGenericAdaptor<::mlir::ValueRange> {
public:
  using ExperimentalCheckOutstandingWritesOpGenericAdaptor::ExperimentalCheckOutstandingWritesOpGenericAdaptor;
  ExperimentalCheckOutstandingWritesOpAdaptor(ExperimentalCheckOutstandingWritesOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class ExperimentalCheckOutstandingWritesOp : public ::mlir::Op<ExperimentalCheckOutstandingWritesOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<3>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ExperimentalCheckOutstandingWritesOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = ExperimentalCheckOutstandingWritesOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_buf = 0;
  static constexpr int odsIndex_buffers = 1;
  static constexpr int odsIndex_writeBars = 2;
  static constexpr int odsIndex_pred = 3;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("writeBarsType")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getWriteBarsTypeAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getWriteBarsTypeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("tti.experimental_check_outstanding_writes");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::triton::gpu::MemDescType> getBuf() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::MemDescType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getBuffers() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::Type> getWriteBars() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::Type>>(*getODSOperands(2).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getPred() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ::mlir::TypedValue<::mlir::IntegerType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*operands.begin());
  }

  ::mlir::OpOperand &getBufMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBuffersMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getWriteBarsMutable() {
    auto range = getODSOperandIndexAndLength(2);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getPredMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::TypeAttr getWriteBarsTypeAttr() {
    return ::llvm::cast<::mlir::TypeAttr>(getProperties().writeBarsType);
  }

  ::mlir::Type getWriteBarsType();
  void setWriteBarsTypeAttr(::mlir::TypeAttr attr) {
    getProperties().writeBarsType = attr;
  }

  void setWriteBarsType(::mlir::Type attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingWritesOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingWritesOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingWritesOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingWritesOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingWritesOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingWritesOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingWritesOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckOutstandingWritesOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalCheckOutstandingWritesOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalCheckOutstandingWritesOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalCheckOutstandingWritesOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalCheckOutstandingWritesOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace instrument
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::instrument::ExperimentalCheckOutstandingWritesOp)

namespace mlir {
namespace triton {
namespace instrument {

//===----------------------------------------------------------------------===//
// ::mlir::triton::instrument::ExperimentalCheckWriteCommitOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class ExperimentalCheckWriteCommitOpGenericAdaptorBase {
public:
  struct Properties {
    using writeCommitsTypeTy = ::mlir::TypeAttr;
    writeCommitsTypeTy writeCommitsType;

    auto getWriteCommitsType() const {
      auto &propStorage = this->writeCommitsType;
      return ::llvm::cast<::mlir::TypeAttr>(propStorage);
    }
    void setWriteCommitsType(const ::mlir::TypeAttr &propValue) {
      this->writeCommitsType = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.writeCommitsType == this->writeCommitsType &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  ExperimentalCheckWriteCommitOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("tti.experimental_check_write_commit", odsAttrs.getContext());
  }

  ExperimentalCheckWriteCommitOpGenericAdaptorBase(ExperimentalCheckWriteCommitOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::TypeAttr getWriteCommitsTypeAttr() {
    auto attr = ::llvm::cast<::mlir::TypeAttr>(getProperties().writeCommitsType);
    return attr;
  }

  ::mlir::Type getWriteCommitsType();
};
} // namespace detail
template <typename RangeT>
class ExperimentalCheckWriteCommitOpGenericAdaptor : public detail::ExperimentalCheckWriteCommitOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::ExperimentalCheckWriteCommitOpGenericAdaptorBase;
  static constexpr int odsIndex_buf = 0;
  static constexpr int odsIndex_buffers = 1;
  static constexpr int odsIndex_writeCommits = 2;
  static constexpr int odsIndex_pred = 3;
public:
  ExperimentalCheckWriteCommitOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  ExperimentalCheckWriteCommitOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : ExperimentalCheckWriteCommitOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  ExperimentalCheckWriteCommitOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : ExperimentalCheckWriteCommitOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  ExperimentalCheckWriteCommitOpGenericAdaptor(RangeT values, const ExperimentalCheckWriteCommitOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = ExperimentalCheckWriteCommitOp, typename = std::enable_if_t<std::is_same_v<LateInst, ExperimentalCheckWriteCommitOp>>>
  ExperimentalCheckWriteCommitOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getBuf() {
    return (*getODSOperands(0).begin());
  }

  ValueT getBuffers() {
    return (*getODSOperands(1).begin());
  }

  ValueT getWriteCommits() {
    return (*getODSOperands(2).begin());
  }

  ValueT getPred() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class ExperimentalCheckWriteCommitOpAdaptor : public ExperimentalCheckWriteCommitOpGenericAdaptor<::mlir::ValueRange> {
public:
  using ExperimentalCheckWriteCommitOpGenericAdaptor::ExperimentalCheckWriteCommitOpGenericAdaptor;
  ExperimentalCheckWriteCommitOpAdaptor(ExperimentalCheckWriteCommitOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class ExperimentalCheckWriteCommitOp : public ::mlir::Op<ExperimentalCheckWriteCommitOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<3>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ExperimentalCheckWriteCommitOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = ExperimentalCheckWriteCommitOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_buf = 0;
  static constexpr int odsIndex_buffers = 1;
  static constexpr int odsIndex_writeCommits = 2;
  static constexpr int odsIndex_pred = 3;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("writeCommitsType")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getWriteCommitsTypeAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getWriteCommitsTypeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("tti.experimental_check_write_commit");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::triton::gpu::MemDescType> getBuf() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::MemDescType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getBuffers() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::Type> getWriteCommits() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::Type>>(*getODSOperands(2).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getPred() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ::mlir::TypedValue<::mlir::IntegerType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*operands.begin());
  }

  ::mlir::OpOperand &getBufMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBuffersMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getWriteCommitsMutable() {
    auto range = getODSOperandIndexAndLength(2);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getPredMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::TypeAttr getWriteCommitsTypeAttr() {
    return ::llvm::cast<::mlir::TypeAttr>(getProperties().writeCommitsType);
  }

  ::mlir::Type getWriteCommitsType();
  void setWriteCommitsTypeAttr(::mlir::TypeAttr attr) {
    getProperties().writeCommitsType = attr;
  }

  void setWriteCommitsType(::mlir::Type attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckWriteCommitOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckWriteCommitOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckWriteCommitOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckWriteCommitOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckWriteCommitOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckWriteCommitOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckWriteCommitOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCheckWriteCommitOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalCheckWriteCommitOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalCheckWriteCommitOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalCheckWriteCommitOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalCheckWriteCommitOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace instrument
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::instrument::ExperimentalCheckWriteCommitOp)

namespace mlir {
namespace triton {
namespace instrument {

//===----------------------------------------------------------------------===//
// ::mlir::triton::instrument::ExperimentalClearReadBarrierOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class ExperimentalClearReadBarrierOpGenericAdaptorBase {
public:
  struct Properties {
    using readBarsTypeTy = ::mlir::TypeAttr;
    readBarsTypeTy readBarsType;

    auto getReadBarsType() const {
      auto &propStorage = this->readBarsType;
      return ::llvm::cast<::mlir::TypeAttr>(propStorage);
    }
    void setReadBarsType(const ::mlir::TypeAttr &propValue) {
      this->readBarsType = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.readBarsType == this->readBarsType &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  ExperimentalClearReadBarrierOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("tti.experimental_clear_read_barrier", odsAttrs.getContext());
  }

  ExperimentalClearReadBarrierOpGenericAdaptorBase(ExperimentalClearReadBarrierOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::TypeAttr getReadBarsTypeAttr() {
    auto attr = ::llvm::cast<::mlir::TypeAttr>(getProperties().readBarsType);
    return attr;
  }

  ::mlir::Type getReadBarsType();
};
} // namespace detail
template <typename RangeT>
class ExperimentalClearReadBarrierOpGenericAdaptor : public detail::ExperimentalClearReadBarrierOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::ExperimentalClearReadBarrierOpGenericAdaptorBase;
  static constexpr int odsIndex_mbar = 0;
  static constexpr int odsIndex_barriers = 1;
  static constexpr int odsIndex_readBars = 2;
  static constexpr int odsIndex_pred = 3;
public:
  ExperimentalClearReadBarrierOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  ExperimentalClearReadBarrierOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : ExperimentalClearReadBarrierOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  ExperimentalClearReadBarrierOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : ExperimentalClearReadBarrierOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  ExperimentalClearReadBarrierOpGenericAdaptor(RangeT values, const ExperimentalClearReadBarrierOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = ExperimentalClearReadBarrierOp, typename = std::enable_if_t<std::is_same_v<LateInst, ExperimentalClearReadBarrierOp>>>
  ExperimentalClearReadBarrierOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getMbar() {
    return (*getODSOperands(0).begin());
  }

  ValueT getBarriers() {
    return (*getODSOperands(1).begin());
  }

  ValueT getReadBars() {
    return (*getODSOperands(2).begin());
  }

  ValueT getPred() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class ExperimentalClearReadBarrierOpAdaptor : public ExperimentalClearReadBarrierOpGenericAdaptor<::mlir::ValueRange> {
public:
  using ExperimentalClearReadBarrierOpGenericAdaptor::ExperimentalClearReadBarrierOpGenericAdaptor;
  ExperimentalClearReadBarrierOpAdaptor(ExperimentalClearReadBarrierOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class ExperimentalClearReadBarrierOp : public ::mlir::Op<ExperimentalClearReadBarrierOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<3>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ExperimentalClearReadBarrierOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = ExperimentalClearReadBarrierOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_mbar = 0;
  static constexpr int odsIndex_barriers = 1;
  static constexpr int odsIndex_readBars = 2;
  static constexpr int odsIndex_pred = 3;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("readBarsType")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getReadBarsTypeAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getReadBarsTypeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("tti.experimental_clear_read_barrier");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::triton::gpu::MemDescType> getMbar() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::MemDescType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getBarriers() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::Type> getReadBars() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::Type>>(*getODSOperands(2).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getPred() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ::mlir::TypedValue<::mlir::IntegerType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*operands.begin());
  }

  ::mlir::OpOperand &getMbarMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBarriersMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getReadBarsMutable() {
    auto range = getODSOperandIndexAndLength(2);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getPredMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::TypeAttr getReadBarsTypeAttr() {
    return ::llvm::cast<::mlir::TypeAttr>(getProperties().readBarsType);
  }

  ::mlir::Type getReadBarsType();
  void setReadBarsTypeAttr(::mlir::TypeAttr attr) {
    getProperties().readBarsType = attr;
  }

  void setReadBarsType(::mlir::Type attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value mbar, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearReadBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value mbar, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearReadBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value mbar, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value mbar, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearReadBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value mbar, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearReadBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value mbar, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value mbar, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearReadBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value mbar, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearReadBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value mbar, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value mbar, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearReadBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value mbar, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearReadBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value mbar, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalClearReadBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalClearReadBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalClearReadBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalClearReadBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace instrument
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::instrument::ExperimentalClearReadBarrierOp)

namespace mlir {
namespace triton {
namespace instrument {

//===----------------------------------------------------------------------===//
// ::mlir::triton::instrument::ExperimentalClearWriteBarrierOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class ExperimentalClearWriteBarrierOpGenericAdaptorBase {
public:
  struct Properties {
    using writeBarsTypeTy = ::mlir::TypeAttr;
    writeBarsTypeTy writeBarsType;

    auto getWriteBarsType() const {
      auto &propStorage = this->writeBarsType;
      return ::llvm::cast<::mlir::TypeAttr>(propStorage);
    }
    void setWriteBarsType(const ::mlir::TypeAttr &propValue) {
      this->writeBarsType = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.writeBarsType == this->writeBarsType &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  ExperimentalClearWriteBarrierOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("tti.experimental_clear_write_barrier", odsAttrs.getContext());
  }

  ExperimentalClearWriteBarrierOpGenericAdaptorBase(ExperimentalClearWriteBarrierOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::TypeAttr getWriteBarsTypeAttr() {
    auto attr = ::llvm::cast<::mlir::TypeAttr>(getProperties().writeBarsType);
    return attr;
  }

  ::mlir::Type getWriteBarsType();
};
} // namespace detail
template <typename RangeT>
class ExperimentalClearWriteBarrierOpGenericAdaptor : public detail::ExperimentalClearWriteBarrierOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::ExperimentalClearWriteBarrierOpGenericAdaptorBase;
  static constexpr int odsIndex_mbar = 0;
  static constexpr int odsIndex_writeBars = 1;
  static constexpr int odsIndex_pred = 2;
public:
  ExperimentalClearWriteBarrierOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  ExperimentalClearWriteBarrierOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : ExperimentalClearWriteBarrierOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  ExperimentalClearWriteBarrierOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : ExperimentalClearWriteBarrierOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  ExperimentalClearWriteBarrierOpGenericAdaptor(RangeT values, const ExperimentalClearWriteBarrierOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = ExperimentalClearWriteBarrierOp, typename = std::enable_if_t<std::is_same_v<LateInst, ExperimentalClearWriteBarrierOp>>>
  ExperimentalClearWriteBarrierOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getMbar() {
    return (*getODSOperands(0).begin());
  }

  ValueT getWriteBars() {
    return (*getODSOperands(1).begin());
  }

  ValueT getPred() {
    auto operands = getODSOperands(2);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class ExperimentalClearWriteBarrierOpAdaptor : public ExperimentalClearWriteBarrierOpGenericAdaptor<::mlir::ValueRange> {
public:
  using ExperimentalClearWriteBarrierOpGenericAdaptor::ExperimentalClearWriteBarrierOpGenericAdaptor;
  ExperimentalClearWriteBarrierOpAdaptor(ExperimentalClearWriteBarrierOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class ExperimentalClearWriteBarrierOp : public ::mlir::Op<ExperimentalClearWriteBarrierOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<2>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ExperimentalClearWriteBarrierOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = ExperimentalClearWriteBarrierOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_mbar = 0;
  static constexpr int odsIndex_writeBars = 1;
  static constexpr int odsIndex_pred = 2;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("writeBarsType")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getWriteBarsTypeAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getWriteBarsTypeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("tti.experimental_clear_write_barrier");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::triton::gpu::MemDescType> getMbar() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::MemDescType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::Type> getWriteBars() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::Type>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getPred() {
    auto operands = getODSOperands(2);
    return operands.empty() ? ::mlir::TypedValue<::mlir::IntegerType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*operands.begin());
  }

  ::mlir::OpOperand &getMbarMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getWriteBarsMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getPredMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::TypeAttr getWriteBarsTypeAttr() {
    return ::llvm::cast<::mlir::TypeAttr>(getProperties().writeBarsType);
  }

  ::mlir::Type getWriteBarsType();
  void setWriteBarsTypeAttr(::mlir::TypeAttr attr) {
    getProperties().writeBarsType = attr;
  }

  void setWriteBarsType(::mlir::Type attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value mbar, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value mbar, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value mbar, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value mbar, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value mbar, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value mbar, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value mbar, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value mbar, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value mbar, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value mbar, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value mbar, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value mbar, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalClearWriteBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalClearWriteBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalClearWriteBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalClearWriteBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace instrument
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::instrument::ExperimentalClearWriteBarrierOp)

namespace mlir {
namespace triton {
namespace instrument {

//===----------------------------------------------------------------------===//
// ::mlir::triton::instrument::ExperimentalClearWriteCommitsOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class ExperimentalClearWriteCommitsOpGenericAdaptorBase {
public:
  struct Properties {
    using outstandingNumTy = ::mlir::IntegerAttr;
    outstandingNumTy outstandingNum;

    auto getOutstandingNum() const {
      auto &propStorage = this->outstandingNum;
      return ::llvm::cast<::mlir::IntegerAttr>(propStorage);
    }
    void setOutstandingNum(const ::mlir::IntegerAttr &propValue) {
      this->outstandingNum = propValue;
    }
    using writeCommitsTypeTy = ::mlir::TypeAttr;
    writeCommitsTypeTy writeCommitsType;

    auto getWriteCommitsType() const {
      auto &propStorage = this->writeCommitsType;
      return ::llvm::cast<::mlir::TypeAttr>(propStorage);
    }
    void setWriteCommitsType(const ::mlir::TypeAttr &propValue) {
      this->writeCommitsType = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.outstandingNum == this->outstandingNum &&
        rhs.writeCommitsType == this->writeCommitsType &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  ExperimentalClearWriteCommitsOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("tti.experimental_clear_write_commits", odsAttrs.getContext());
  }

  ExperimentalClearWriteCommitsOpGenericAdaptorBase(ExperimentalClearWriteCommitsOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::TypeAttr getWriteCommitsTypeAttr() {
    auto attr = ::llvm::cast<::mlir::TypeAttr>(getProperties().writeCommitsType);
    return attr;
  }

  ::mlir::Type getWriteCommitsType();
  ::mlir::IntegerAttr getOutstandingNumAttr() {
    auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().outstandingNum);
    return attr;
  }

  uint32_t getOutstandingNum();
};
} // namespace detail
template <typename RangeT>
class ExperimentalClearWriteCommitsOpGenericAdaptor : public detail::ExperimentalClearWriteCommitsOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::ExperimentalClearWriteCommitsOpGenericAdaptorBase;
  static constexpr int odsIndex_writeCommits = 0;
  static constexpr int odsIndex_pred = 1;
public:
  ExperimentalClearWriteCommitsOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  ExperimentalClearWriteCommitsOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : ExperimentalClearWriteCommitsOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  ExperimentalClearWriteCommitsOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : ExperimentalClearWriteCommitsOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  ExperimentalClearWriteCommitsOpGenericAdaptor(RangeT values, const ExperimentalClearWriteCommitsOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = ExperimentalClearWriteCommitsOp, typename = std::enable_if_t<std::is_same_v<LateInst, ExperimentalClearWriteCommitsOp>>>
  ExperimentalClearWriteCommitsOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getWriteCommits() {
    return (*getODSOperands(0).begin());
  }

  ValueT getPred() {
    auto operands = getODSOperands(1);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class ExperimentalClearWriteCommitsOpAdaptor : public ExperimentalClearWriteCommitsOpGenericAdaptor<::mlir::ValueRange> {
public:
  using ExperimentalClearWriteCommitsOpGenericAdaptor::ExperimentalClearWriteCommitsOpGenericAdaptor;
  ExperimentalClearWriteCommitsOpAdaptor(ExperimentalClearWriteCommitsOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class ExperimentalClearWriteCommitsOp : public ::mlir::Op<ExperimentalClearWriteCommitsOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<1>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ExperimentalClearWriteCommitsOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = ExperimentalClearWriteCommitsOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_writeCommits = 0;
  static constexpr int odsIndex_pred = 1;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("outstandingNum"), ::llvm::StringRef("writeCommitsType")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getOutstandingNumAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getOutstandingNumAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr getWriteCommitsTypeAttrName() {
    return getAttributeNameForIndex(1);
  }

  static ::mlir::StringAttr getWriteCommitsTypeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 1);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("tti.experimental_clear_write_commits");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::Type> getWriteCommits() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::Type>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getPred() {
    auto operands = getODSOperands(1);
    return operands.empty() ? ::mlir::TypedValue<::mlir::IntegerType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*operands.begin());
  }

  ::mlir::OpOperand &getWriteCommitsMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getPredMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::TypeAttr getWriteCommitsTypeAttr() {
    return ::llvm::cast<::mlir::TypeAttr>(getProperties().writeCommitsType);
  }

  ::mlir::Type getWriteCommitsType();
  ::mlir::IntegerAttr getOutstandingNumAttr() {
    return ::llvm::cast<::mlir::IntegerAttr>(getProperties().outstandingNum);
  }

  uint32_t getOutstandingNum();
  void setWriteCommitsTypeAttr(::mlir::TypeAttr attr) {
    getProperties().writeCommitsType = attr;
  }

  void setWriteCommitsType(::mlir::Type attrValue);
  void setOutstandingNumAttr(::mlir::IntegerAttr attr) {
    getProperties().outstandingNum = attr;
  }

  void setOutstandingNum(uint32_t attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, ::mlir::IntegerAttr outstandingNum, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteCommitsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, ::mlir::IntegerAttr outstandingNum, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteCommitsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, ::mlir::IntegerAttr outstandingNum, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, ::mlir::IntegerAttr outstandingNum, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteCommitsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, ::mlir::IntegerAttr outstandingNum, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteCommitsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, ::mlir::IntegerAttr outstandingNum, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, uint32_t outstandingNum, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteCommitsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, uint32_t outstandingNum, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteCommitsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, uint32_t outstandingNum, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, uint32_t outstandingNum, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteCommitsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, uint32_t outstandingNum, /*optional*/::mlir::Value pred);
  static ExperimentalClearWriteCommitsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, uint32_t outstandingNum, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalClearWriteCommitsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalClearWriteCommitsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalClearWriteCommitsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalClearWriteCommitsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 2 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace instrument
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::instrument::ExperimentalClearWriteCommitsOp)

namespace mlir {
namespace triton {
namespace instrument {

//===----------------------------------------------------------------------===//
// ::mlir::triton::instrument::ExperimentalCommitWritesOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class ExperimentalCommitWritesOpGenericAdaptorBase {
public:
  struct Properties {
    using writeCommitsTypeTy = ::mlir::TypeAttr;
    writeCommitsTypeTy writeCommitsType;

    auto getWriteCommitsType() const {
      auto &propStorage = this->writeCommitsType;
      return ::llvm::cast<::mlir::TypeAttr>(propStorage);
    }
    void setWriteCommitsType(const ::mlir::TypeAttr &propValue) {
      this->writeCommitsType = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.writeCommitsType == this->writeCommitsType &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  ExperimentalCommitWritesOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("tti.experimental_commit_writes", odsAttrs.getContext());
  }

  ExperimentalCommitWritesOpGenericAdaptorBase(ExperimentalCommitWritesOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::TypeAttr getWriteCommitsTypeAttr() {
    auto attr = ::llvm::cast<::mlir::TypeAttr>(getProperties().writeCommitsType);
    return attr;
  }

  ::mlir::Type getWriteCommitsType();
};
} // namespace detail
template <typename RangeT>
class ExperimentalCommitWritesOpGenericAdaptor : public detail::ExperimentalCommitWritesOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::ExperimentalCommitWritesOpGenericAdaptorBase;
  static constexpr int odsIndex_writeCommits = 0;
  static constexpr int odsIndex_pred = 1;
public:
  ExperimentalCommitWritesOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  ExperimentalCommitWritesOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : ExperimentalCommitWritesOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  ExperimentalCommitWritesOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : ExperimentalCommitWritesOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  ExperimentalCommitWritesOpGenericAdaptor(RangeT values, const ExperimentalCommitWritesOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = ExperimentalCommitWritesOp, typename = std::enable_if_t<std::is_same_v<LateInst, ExperimentalCommitWritesOp>>>
  ExperimentalCommitWritesOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getWriteCommits() {
    return (*getODSOperands(0).begin());
  }

  ValueT getPred() {
    auto operands = getODSOperands(1);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class ExperimentalCommitWritesOpAdaptor : public ExperimentalCommitWritesOpGenericAdaptor<::mlir::ValueRange> {
public:
  using ExperimentalCommitWritesOpGenericAdaptor::ExperimentalCommitWritesOpGenericAdaptor;
  ExperimentalCommitWritesOpAdaptor(ExperimentalCommitWritesOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class ExperimentalCommitWritesOp : public ::mlir::Op<ExperimentalCommitWritesOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<1>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ExperimentalCommitWritesOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = ExperimentalCommitWritesOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_writeCommits = 0;
  static constexpr int odsIndex_pred = 1;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("writeCommitsType")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getWriteCommitsTypeAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getWriteCommitsTypeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("tti.experimental_commit_writes");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::Type> getWriteCommits() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::Type>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getPred() {
    auto operands = getODSOperands(1);
    return operands.empty() ? ::mlir::TypedValue<::mlir::IntegerType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*operands.begin());
  }

  ::mlir::OpOperand &getWriteCommitsMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getPredMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::TypeAttr getWriteCommitsTypeAttr() {
    return ::llvm::cast<::mlir::TypeAttr>(getProperties().writeCommitsType);
  }

  ::mlir::Type getWriteCommitsType();
  void setWriteCommitsTypeAttr(::mlir::TypeAttr attr) {
    getProperties().writeCommitsType = attr;
  }

  void setWriteCommitsType(::mlir::Type attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCommitWritesOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCommitWritesOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCommitWritesOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCommitWritesOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCommitWritesOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCommitWritesOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCommitWritesOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalCommitWritesOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalCommitWritesOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalCommitWritesOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalCommitWritesOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalCommitWritesOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace instrument
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::instrument::ExperimentalCommitWritesOp)

namespace mlir {
namespace triton {
namespace instrument {

//===----------------------------------------------------------------------===//
// ::mlir::triton::instrument::ExperimentalMarkAsReadOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class ExperimentalMarkAsReadOpGenericAdaptorBase {
public:
  struct Properties {
    using readBarsTypeTy = ::mlir::TypeAttr;
    readBarsTypeTy readBarsType;

    auto getReadBarsType() const {
      auto &propStorage = this->readBarsType;
      return ::llvm::cast<::mlir::TypeAttr>(propStorage);
    }
    void setReadBarsType(const ::mlir::TypeAttr &propValue) {
      this->readBarsType = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.readBarsType == this->readBarsType &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  ExperimentalMarkAsReadOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("tti.experimental_mark_as_read", odsAttrs.getContext());
  }

  ExperimentalMarkAsReadOpGenericAdaptorBase(ExperimentalMarkAsReadOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::TypeAttr getReadBarsTypeAttr() {
    auto attr = ::llvm::cast<::mlir::TypeAttr>(getProperties().readBarsType);
    return attr;
  }

  ::mlir::Type getReadBarsType();
};
} // namespace detail
template <typename RangeT>
class ExperimentalMarkAsReadOpGenericAdaptor : public detail::ExperimentalMarkAsReadOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::ExperimentalMarkAsReadOpGenericAdaptorBase;
  static constexpr int odsIndex_buf = 0;
  static constexpr int odsIndex_mbar = 1;
  static constexpr int odsIndex_buffers = 2;
  static constexpr int odsIndex_barriers = 3;
  static constexpr int odsIndex_readBars = 4;
  static constexpr int odsIndex_pred = 5;
public:
  ExperimentalMarkAsReadOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  ExperimentalMarkAsReadOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : ExperimentalMarkAsReadOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  ExperimentalMarkAsReadOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : ExperimentalMarkAsReadOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  ExperimentalMarkAsReadOpGenericAdaptor(RangeT values, const ExperimentalMarkAsReadOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = ExperimentalMarkAsReadOp, typename = std::enable_if_t<std::is_same_v<LateInst, ExperimentalMarkAsReadOp>>>
  ExperimentalMarkAsReadOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getBuf() {
    return (*getODSOperands(0).begin());
  }

  ValueT getMbar() {
    return (*getODSOperands(1).begin());
  }

  ValueT getBuffers() {
    return (*getODSOperands(2).begin());
  }

  ValueT getBarriers() {
    return (*getODSOperands(3).begin());
  }

  ValueT getReadBars() {
    return (*getODSOperands(4).begin());
  }

  ValueT getPred() {
    auto operands = getODSOperands(5);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class ExperimentalMarkAsReadOpAdaptor : public ExperimentalMarkAsReadOpGenericAdaptor<::mlir::ValueRange> {
public:
  using ExperimentalMarkAsReadOpGenericAdaptor::ExperimentalMarkAsReadOpGenericAdaptor;
  ExperimentalMarkAsReadOpAdaptor(ExperimentalMarkAsReadOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class ExperimentalMarkAsReadOp : public ::mlir::Op<ExperimentalMarkAsReadOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<5>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ExperimentalMarkAsReadOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = ExperimentalMarkAsReadOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_buf = 0;
  static constexpr int odsIndex_mbar = 1;
  static constexpr int odsIndex_buffers = 2;
  static constexpr int odsIndex_barriers = 3;
  static constexpr int odsIndex_readBars = 4;
  static constexpr int odsIndex_pred = 5;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("readBarsType")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getReadBarsTypeAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getReadBarsTypeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("tti.experimental_mark_as_read");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::triton::gpu::MemDescType> getBuf() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::MemDescType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::triton::gpu::MemDescType> getMbar() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::MemDescType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getBuffers() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(2).begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getBarriers() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(3).begin());
  }

  ::mlir::TypedValue<::mlir::Type> getReadBars() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::Type>>(*getODSOperands(4).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getPred() {
    auto operands = getODSOperands(5);
    return operands.empty() ? ::mlir::TypedValue<::mlir::IntegerType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*operands.begin());
  }

  ::mlir::OpOperand &getBufMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getMbarMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBuffersMutable() {
    auto range = getODSOperandIndexAndLength(2);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBarriersMutable() {
    auto range = getODSOperandIndexAndLength(3);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getReadBarsMutable() {
    auto range = getODSOperandIndexAndLength(4);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getPredMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::TypeAttr getReadBarsTypeAttr() {
    return ::llvm::cast<::mlir::TypeAttr>(getProperties().readBarsType);
  }

  ::mlir::Type getReadBarsType();
  void setReadBarsTypeAttr(::mlir::TypeAttr attr) {
    getProperties().readBarsType = attr;
  }

  void setReadBarsType(::mlir::Type attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsReadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsReadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsReadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsReadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::TypeAttr readBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsReadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsReadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsReadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsReadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value barriers, ::mlir::Value readBars, ::mlir::Type readBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalMarkAsReadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalMarkAsReadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalMarkAsReadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalMarkAsReadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace instrument
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::instrument::ExperimentalMarkAsReadOp)

namespace mlir {
namespace triton {
namespace instrument {

//===----------------------------------------------------------------------===//
// ::mlir::triton::instrument::ExperimentalMarkAsWriteOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class ExperimentalMarkAsWriteOpGenericAdaptorBase {
public:
  struct Properties {
    using writeBarsTypeTy = ::mlir::TypeAttr;
    writeBarsTypeTy writeBarsType;

    auto getWriteBarsType() const {
      auto &propStorage = this->writeBarsType;
      return ::llvm::cast<::mlir::TypeAttr>(propStorage);
    }
    void setWriteBarsType(const ::mlir::TypeAttr &propValue) {
      this->writeBarsType = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.writeBarsType == this->writeBarsType &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  ExperimentalMarkAsWriteOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("tti.experimental_mark_as_write", odsAttrs.getContext());
  }

  ExperimentalMarkAsWriteOpGenericAdaptorBase(ExperimentalMarkAsWriteOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::TypeAttr getWriteBarsTypeAttr() {
    auto attr = ::llvm::cast<::mlir::TypeAttr>(getProperties().writeBarsType);
    return attr;
  }

  ::mlir::Type getWriteBarsType();
};
} // namespace detail
template <typename RangeT>
class ExperimentalMarkAsWriteOpGenericAdaptor : public detail::ExperimentalMarkAsWriteOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::ExperimentalMarkAsWriteOpGenericAdaptorBase;
  static constexpr int odsIndex_buf = 0;
  static constexpr int odsIndex_mbar = 1;
  static constexpr int odsIndex_buffers = 2;
  static constexpr int odsIndex_writeBars = 3;
  static constexpr int odsIndex_pred = 4;
public:
  ExperimentalMarkAsWriteOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  ExperimentalMarkAsWriteOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : ExperimentalMarkAsWriteOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  ExperimentalMarkAsWriteOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : ExperimentalMarkAsWriteOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  ExperimentalMarkAsWriteOpGenericAdaptor(RangeT values, const ExperimentalMarkAsWriteOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = ExperimentalMarkAsWriteOp, typename = std::enable_if_t<std::is_same_v<LateInst, ExperimentalMarkAsWriteOp>>>
  ExperimentalMarkAsWriteOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getBuf() {
    return (*getODSOperands(0).begin());
  }

  ValueT getMbar() {
    return (*getODSOperands(1).begin());
  }

  ValueT getBuffers() {
    return (*getODSOperands(2).begin());
  }

  ValueT getWriteBars() {
    return (*getODSOperands(3).begin());
  }

  ValueT getPred() {
    auto operands = getODSOperands(4);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class ExperimentalMarkAsWriteOpAdaptor : public ExperimentalMarkAsWriteOpGenericAdaptor<::mlir::ValueRange> {
public:
  using ExperimentalMarkAsWriteOpGenericAdaptor::ExperimentalMarkAsWriteOpGenericAdaptor;
  ExperimentalMarkAsWriteOpAdaptor(ExperimentalMarkAsWriteOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class ExperimentalMarkAsWriteOp : public ::mlir::Op<ExperimentalMarkAsWriteOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<4>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ExperimentalMarkAsWriteOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = ExperimentalMarkAsWriteOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_buf = 0;
  static constexpr int odsIndex_mbar = 1;
  static constexpr int odsIndex_buffers = 2;
  static constexpr int odsIndex_writeBars = 3;
  static constexpr int odsIndex_pred = 4;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("writeBarsType")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getWriteBarsTypeAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getWriteBarsTypeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("tti.experimental_mark_as_write");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::triton::gpu::MemDescType> getBuf() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::MemDescType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::triton::gpu::MemDescType> getMbar() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::MemDescType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getBuffers() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(2).begin());
  }

  ::mlir::TypedValue<::mlir::Type> getWriteBars() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::Type>>(*getODSOperands(3).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getPred() {
    auto operands = getODSOperands(4);
    return operands.empty() ? ::mlir::TypedValue<::mlir::IntegerType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*operands.begin());
  }

  ::mlir::OpOperand &getBufMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getMbarMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBuffersMutable() {
    auto range = getODSOperandIndexAndLength(2);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getWriteBarsMutable() {
    auto range = getODSOperandIndexAndLength(3);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getPredMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::TypeAttr getWriteBarsTypeAttr() {
    return ::llvm::cast<::mlir::TypeAttr>(getProperties().writeBarsType);
  }

  ::mlir::Type getWriteBarsType();
  void setWriteBarsTypeAttr(::mlir::TypeAttr attr) {
    getProperties().writeBarsType = attr;
  }

  void setWriteBarsType(::mlir::Type attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsWriteOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsWriteOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsWriteOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsWriteOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::TypeAttr writeBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsWriteOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsWriteOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsWriteOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static ExperimentalMarkAsWriteOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value mbar, ::mlir::Value buffers, ::mlir::Value writeBars, ::mlir::Type writeBarsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalMarkAsWriteOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalMarkAsWriteOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalMarkAsWriteOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalMarkAsWriteOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace instrument
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::instrument::ExperimentalMarkAsWriteOp)

namespace mlir {
namespace triton {
namespace instrument {

//===----------------------------------------------------------------------===//
// ::mlir::triton::instrument::ExperimentalSharedBufferPointersOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class ExperimentalSharedBufferPointersOpGenericAdaptorBase {
public:
  struct Properties {
    using offsetsTy = ::mlir::DenseI32ArrayAttr;
    offsetsTy offsets;

    auto getOffsets() const {
      auto &propStorage = this->offsets;
      return ::llvm::cast<::mlir::DenseI32ArrayAttr>(propStorage);
    }
    void setOffsets(const ::mlir::DenseI32ArrayAttr &propValue) {
      this->offsets = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.offsets == this->offsets &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  ExperimentalSharedBufferPointersOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("tti.experimental_shared_buffer_pointers", odsAttrs.getContext());
  }

  ExperimentalSharedBufferPointersOpGenericAdaptorBase(ExperimentalSharedBufferPointersOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
    return {index, 1};
  }

  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::DenseI32ArrayAttr getOffsetsAttr() {
    auto attr = ::llvm::cast<::mlir::DenseI32ArrayAttr>(getProperties().offsets);
    return attr;
  }

  ::llvm::ArrayRef<int32_t> getOffsets();
};
} // namespace detail
template <typename RangeT>
class ExperimentalSharedBufferPointersOpGenericAdaptor : public detail::ExperimentalSharedBufferPointersOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::ExperimentalSharedBufferPointersOpGenericAdaptorBase;
public:
  ExperimentalSharedBufferPointersOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  ExperimentalSharedBufferPointersOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : ExperimentalSharedBufferPointersOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  ExperimentalSharedBufferPointersOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : ExperimentalSharedBufferPointersOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  ExperimentalSharedBufferPointersOpGenericAdaptor(RangeT values, const ExperimentalSharedBufferPointersOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = ExperimentalSharedBufferPointersOp, typename = std::enable_if_t<std::is_same_v<LateInst, ExperimentalSharedBufferPointersOp>>>
  ExperimentalSharedBufferPointersOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class ExperimentalSharedBufferPointersOpAdaptor : public ExperimentalSharedBufferPointersOpGenericAdaptor<::mlir::ValueRange> {
public:
  using ExperimentalSharedBufferPointersOpGenericAdaptor::ExperimentalSharedBufferPointersOpGenericAdaptor;
  ExperimentalSharedBufferPointersOpAdaptor(ExperimentalSharedBufferPointersOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class ExperimentalSharedBufferPointersOp : public ::mlir::Op<ExperimentalSharedBufferPointersOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::OneResult, ::mlir::OpTrait::OneTypedResult<::mlir::RankedTensorType>::Impl, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::ZeroOperands, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::ConditionallySpeculatable::Trait, ::mlir::OpTrait::AlwaysSpeculatableImplTrait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ExperimentalSharedBufferPointersOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = ExperimentalSharedBufferPointersOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("offsets")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getOffsetsAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getOffsetsAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("tti.experimental_shared_buffer_pointers");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getResult() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSResults(0).begin());
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::DenseI32ArrayAttr getOffsetsAttr() {
    return ::llvm::cast<::mlir::DenseI32ArrayAttr>(getProperties().offsets);
  }

  ::llvm::ArrayRef<int32_t> getOffsets();
  void setOffsetsAttr(::mlir::DenseI32ArrayAttr attr) {
    getProperties().offsets = attr;
  }

  void setOffsets(::llvm::ArrayRef<int32_t> attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::DenseI32ArrayAttr offsets);
  static ExperimentalSharedBufferPointersOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::DenseI32ArrayAttr offsets);
  static ExperimentalSharedBufferPointersOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::DenseI32ArrayAttr offsets);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::DenseI32ArrayAttr offsets);
  static ExperimentalSharedBufferPointersOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::DenseI32ArrayAttr offsets);
  static ExperimentalSharedBufferPointersOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::DenseI32ArrayAttr offsets);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::llvm::ArrayRef<int32_t> offsets);
  static ExperimentalSharedBufferPointersOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::llvm::ArrayRef<int32_t> offsets);
  static ExperimentalSharedBufferPointersOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::llvm::ArrayRef<int32_t> offsets);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::llvm::ArrayRef<int32_t> offsets);
  static ExperimentalSharedBufferPointersOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::llvm::ArrayRef<int32_t> offsets);
  static ExperimentalSharedBufferPointersOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::llvm::ArrayRef<int32_t> offsets);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalSharedBufferPointersOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalSharedBufferPointersOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalSharedBufferPointersOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalSharedBufferPointersOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace instrument
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::instrument::ExperimentalSharedBufferPointersOp)

namespace mlir {
namespace triton {
namespace instrument {

//===----------------------------------------------------------------------===//
// ::mlir::triton::instrument::ExperimentalStageWriteForCommitOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class ExperimentalStageWriteForCommitOpGenericAdaptorBase {
public:
  struct Properties {
    using writeCommitsTypeTy = ::mlir::TypeAttr;
    writeCommitsTypeTy writeCommitsType;

    auto getWriteCommitsType() const {
      auto &propStorage = this->writeCommitsType;
      return ::llvm::cast<::mlir::TypeAttr>(propStorage);
    }
    void setWriteCommitsType(const ::mlir::TypeAttr &propValue) {
      this->writeCommitsType = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.writeCommitsType == this->writeCommitsType &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  ExperimentalStageWriteForCommitOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("tti.experimental_stage_write_for_commit", odsAttrs.getContext());
  }

  ExperimentalStageWriteForCommitOpGenericAdaptorBase(ExperimentalStageWriteForCommitOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::TypeAttr getWriteCommitsTypeAttr() {
    auto attr = ::llvm::cast<::mlir::TypeAttr>(getProperties().writeCommitsType);
    return attr;
  }

  ::mlir::Type getWriteCommitsType();
};
} // namespace detail
template <typename RangeT>
class ExperimentalStageWriteForCommitOpGenericAdaptor : public detail::ExperimentalStageWriteForCommitOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::ExperimentalStageWriteForCommitOpGenericAdaptorBase;
  static constexpr int odsIndex_buf = 0;
  static constexpr int odsIndex_buffers = 1;
  static constexpr int odsIndex_writeCommits = 2;
  static constexpr int odsIndex_pred = 3;
public:
  ExperimentalStageWriteForCommitOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  ExperimentalStageWriteForCommitOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : ExperimentalStageWriteForCommitOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  ExperimentalStageWriteForCommitOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : ExperimentalStageWriteForCommitOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  ExperimentalStageWriteForCommitOpGenericAdaptor(RangeT values, const ExperimentalStageWriteForCommitOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = ExperimentalStageWriteForCommitOp, typename = std::enable_if_t<std::is_same_v<LateInst, ExperimentalStageWriteForCommitOp>>>
  ExperimentalStageWriteForCommitOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getBuf() {
    return (*getODSOperands(0).begin());
  }

  ValueT getBuffers() {
    return (*getODSOperands(1).begin());
  }

  ValueT getWriteCommits() {
    return (*getODSOperands(2).begin());
  }

  ValueT getPred() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class ExperimentalStageWriteForCommitOpAdaptor : public ExperimentalStageWriteForCommitOpGenericAdaptor<::mlir::ValueRange> {
public:
  using ExperimentalStageWriteForCommitOpGenericAdaptor::ExperimentalStageWriteForCommitOpGenericAdaptor;
  ExperimentalStageWriteForCommitOpAdaptor(ExperimentalStageWriteForCommitOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class ExperimentalStageWriteForCommitOp : public ::mlir::Op<ExperimentalStageWriteForCommitOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<3>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ExperimentalStageWriteForCommitOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = ExperimentalStageWriteForCommitOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_buf = 0;
  static constexpr int odsIndex_buffers = 1;
  static constexpr int odsIndex_writeCommits = 2;
  static constexpr int odsIndex_pred = 3;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("writeCommitsType")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getWriteCommitsTypeAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getWriteCommitsTypeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("tti.experimental_stage_write_for_commit");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::triton::gpu::MemDescType> getBuf() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::MemDescType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getBuffers() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::Type> getWriteCommits() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::Type>>(*getODSOperands(2).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getPred() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ::mlir::TypedValue<::mlir::IntegerType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*operands.begin());
  }

  ::mlir::OpOperand &getBufMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBuffersMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getWriteCommitsMutable() {
    auto range = getODSOperandIndexAndLength(2);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getPredMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::TypeAttr getWriteCommitsTypeAttr() {
    return ::llvm::cast<::mlir::TypeAttr>(getProperties().writeCommitsType);
  }

  ::mlir::Type getWriteCommitsType();
  void setWriteCommitsTypeAttr(::mlir::TypeAttr attr) {
    getProperties().writeCommitsType = attr;
  }

  void setWriteCommitsType(::mlir::Type attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalStageWriteForCommitOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalStageWriteForCommitOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalStageWriteForCommitOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalStageWriteForCommitOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::TypeAttr writeCommitsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalStageWriteForCommitOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalStageWriteForCommitOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalStageWriteForCommitOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static ExperimentalStageWriteForCommitOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value buf, ::mlir::Value buffers, ::mlir::Value writeCommits, ::mlir::Type writeCommitsType, /*optional*/::mlir::Value pred);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalStageWriteForCommitOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExperimentalStageWriteForCommitOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalStageWriteForCommitOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExperimentalStageWriteForCommitOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace instrument
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::instrument::ExperimentalStageWriteForCommitOp)


#endif  // GET_OP_CLASSES

